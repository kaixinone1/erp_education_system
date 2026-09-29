"""
ERP系统备份监督自愈脚本（独立监督者）
====================================
本脚本独立于后端进程运行，由 Windows 任务计划程序每30分钟唤醒一次。

功能：
1. 后端存活探测 → 挂了自动重启
2. 调度器状态探测 → 未运行自动重启后端（间接重启调度器）
3. 备份时效探测 → 超时自动触发补偿备份
4. 飞书推送有效性探测 → 失败用独立webhook补发告警

设计原则：
- 完全独立于后端进程，不依赖任何后端模块
- 直读JSON状态文件，避免后端API依赖
- 自带独立飞书webhook，后端挂了也能发出告警
- PID锁防止多实例并发
- 告警静默期避免30分钟内重复告警

作者：ERP系统监督机制
日期：2026-09-29
"""
import os
import sys
import json
import time
import socket
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# 第三方依赖
try:
    import requests
except ImportError:
    print("错误：缺少 requests 模块，请运行 pip install requests")
    sys.exit(1)

# ============================================================
# 路径与日志配置
# ============================================================
BASE_DIR = Path(__file__).resolve().parent  # d:\erp_fifteen\supervisor
CONFIG_FILE = BASE_DIR / "config" / "supervisor_config.json"
STATE_DIR = BASE_DIR / "state"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "supervisor.log"
ALERT_FALLBACK_FILE = STATE_DIR / "ALERT_FALLBACK.txt"
ALERT_STATE_FILE = STATE_DIR / "alert_state.json"
DISK_SPACE_STATE_FILE = STATE_DIR / "disk_space_state.json"  # 磁盘空间预警状态（避免24小时内重复预警）

# 确保目录存在
STATE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 日志配置（中文，UTF-8，同时输出到文件和控制台）
_FILE_HANDLER = logging.FileHandler(LOG_FILE, encoding='utf-8')
_FILE_HANDLER.setLevel(logging.INFO)
_FILE_HANDLER.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
))
_CONSOLE_HANDLER = logging.StreamHandler()
_CONSOLE_HANDLER.setLevel(logging.INFO)
_CONSOLE_HANDLER.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
))
logger = logging.getLogger("supervisor")
logger.setLevel(logging.INFO)
logger.addHandler(_FILE_HANDLER)
logger.addHandler(_CONSOLE_HANDLER)


# ============================================================
# 配置加载
# ============================================================
def load_config():
    """加载监督配置"""
    if not CONFIG_FILE.exists():
        logger.error(f"配置文件不存在: {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================
# PID 锁管理（防多实例）
# ============================================================
def acquire_supervisor_lock(lock_file):
    """
    获取监督脚本自身的PID锁，防止多个监督脚本实例同时运行
    返回: True=获取成功, False=已有实例在运行
    """
    lock_file = BASE_DIR / lock_file
    current_pid = os.getpid()

    # 检查现有锁
    if lock_file.exists():
        try:
            old_pid = int(lock_file.read_text(encoding='utf-8').strip())
            if _is_pid_alive(old_pid):
                logger.warning(f"检测到已有监督实例在运行（PID={old_pid}），本次退出")
                return False
            else:
                logger.info(f"旧的监督PID={old_pid} 已死亡，清理锁文件")
                lock_file.unlink(missing_ok=True)
        except (ValueError, OSError):
            # 锁文件损坏，清理
            lock_file.unlink(missing_ok=True)

    # 写入当前PID
    lock_file.write_text(str(current_pid), encoding='utf-8')
    logger.info(f"监督脚本启动，PID={current_pid}")
    return True


def release_supervisor_lock(lock_file):
    """释放监督脚本PID锁"""
    lock_file = BASE_DIR / lock_file
    try:
        lock_file.unlink(missing_ok=True)
    except Exception as e:
        logger.warning(f"清理监督PID锁失败: {e}")


def _is_pid_alive(pid):
    """检查进程是否存活（Windows版）"""
    if pid <= 0:
        return False
    try:
        # Windows: 使用 tasklist 检查进程
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5
        )
        return str(pid) in result.stdout
    except Exception:
        # 回退：尝试 os.kill 的方式
        try:
            import ctypes
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            return False


# ============================================================
# 后端存活探测
# ============================================================
def check_backend_alive(config):
    """
    后端存活探测（HTTP健康检查为主，重试3次避免误报）
    返回: (存活: bool, 详情: str)
    """
    backend_cfg = config["后端"]
    host = backend_cfg["主机"]
    port = backend_cfg["端口"]
    timeout = backend_cfg["请求超时秒"]
    url = f"http://{host}:{port}{backend_cfg['健康检查路径']}"

    # HTTP健康检查为主，重试3次（每次间隔3秒），全部失败才判定挂了
    last_error = None
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                if attempt > 1:
                    logger.info(f"  第{attempt}次HTTP检查成功")
                return True, "后端存活正常"
            else:
                last_error = f"HTTP状态码 {resp.status_code}"
        except requests.exceptions.Timeout:
            last_error = "HTTP超时"
        except requests.exceptions.ConnectionError as e:
            # 连接被拒绝通常意味着后端没在运行
            last_error = f"连接失败: {str(e)[:100]}"
        except Exception as e:
            last_error = f"HTTP检查异常: {e}"

        if attempt < 3:
            logger.info(f"  HTTP第{attempt}次失败: {last_error}，3秒后重试...")
            time.sleep(3)

    return False, f"后端故障（连续3次HTTP检查失败，最后错误: {last_error}）"


def restart_backend(config):
    """
    重启后端服务
    - 使用 pythonw 隐藏窗口启动
    - DETACHED_PROCESS 标志完全脱离父进程
    - 启动后写入新PID，等待30秒再次健康检查
    返回: (成功: bool, 新PID: int|None, 详情: str)
    """
    backend_cfg = config["后端"]
    script_path = backend_cfg["启动脚本"]
    python_exe = backend_cfg["启动方式"]  # pythonw
    wait_seconds = backend_cfg.get("重启后等待秒", 30)
    pid_file = BASE_DIR / backend_cfg["PID文件"]

    if not Path(script_path).exists():
        return False, None, f"启动脚本不存在: {script_path}"

    logger.info(f"正在重启后端，启动脚本: {script_path}")

    try:
        # 隐藏窗口启动
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # DETACHED_PROCESS = 0x00000008, CREATE_NEW_PROCESS_GROUP = 0x00000200
        creationflags = 0x00000008 | 0x00000200

        proc = subprocess.Popen(
            [python_exe, script_path],
            cwd=str(Path(script_path).parent),
            startupinfo=startupinfo,
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True
        )

        new_pid = proc.pid
        # 写入新PID
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(new_pid), encoding='utf-8')
        logger.info(f"后端已启动，新PID={new_pid}，等待 {wait_seconds} 秒后健康检查...")

        # 等待后端完全启动
        time.sleep(wait_seconds)

        # 再次健康检查
        alive, detail = check_backend_alive(config)
        if alive:
            logger.info(f"后端重启成功，健康检查通过")
            return True, new_pid, "后端重启成功"
        else:
            return False, new_pid, f"后端重启后健康检查仍失败: {detail}"

    except Exception as e:
        return False, None, f"重启后端异常: {e}"


# ============================================================
# 前端存活探测 + 自愈
# ============================================================
def check_frontend_alive(config):
    """
    前端存活探测（HTTP健康检查，重试3次）
    返回: (存活: bool, 详情: str)
    """
    if "前端" not in config:
        return True, "未配置前端监督，跳过"
    frontend_cfg = config["前端"]
    host = frontend_cfg["主机"]
    port = frontend_cfg["端口"]
    timeout = frontend_cfg["请求超时秒"]
    url = f"http://{host}:{port}{frontend_cfg['健康检查路径']}"

    last_error = None
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, timeout=timeout)
            # 前端Vite开发服务器默认返回200
            if resp.status_code < 500:
                if attempt > 1:
                    logger.info(f"  前端第{attempt}次检查成功")
                return True, "前端存活正常"
            else:
                last_error = f"HTTP状态码 {resp.status_code}"
        except requests.exceptions.Timeout:
            last_error = "HTTP超时"
        except requests.exceptions.ConnectionError as e:
            last_error = f"连接失败: {str(e)[:100]}"
        except Exception as e:
            last_error = f"HTTP检查异常: {e}"

        if attempt < 3:
            logger.info(f"  前端HTTP第{attempt}次失败: {last_error}，3秒后重试...")
            time.sleep(3)

    return False, f"前端故障（连续3次HTTP检查失败，最后错误: {last_error}）"


def restart_frontend(config):
    """
    重启前端服务（独立于后端重启，不影响后端）
    - 先释放5173端口（kill占用进程）
    - 用 npm run dev 启动
    - 启动后等待40秒再次健康检查
    返回: (成功: bool, 新PID: int|None, 详情: str)
    """
    if "前端" not in config:
        return False, None, "未配置前端监督"
    frontend_cfg = config["前端"]
    frontend_dir = frontend_cfg["前端目录"]
    start_cmd = frontend_cfg["启动命令"]
    start_args = frontend_cfg.get("启动参数", [])
    wait_seconds = frontend_cfg.get("重启后等待秒", 40)
    pid_file = BASE_DIR / frontend_cfg["PID文件"]
    port = frontend_cfg["端口"]

    if not Path(frontend_dir).exists():
        return False, None, f"前端目录不存在: {frontend_dir}"

    logger.info(f"正在重启前端，目录: {frontend_dir}")

    # 先释放端口
    try:
        result = subprocess.run(
            f'netstat -ano | findstr ":{port} " | findstr "LISTENING"',
            shell=True, capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                parts = line.strip().split()
                if len(parts) >= 5:
                    old_pid = parts[-1]
                    subprocess.run(f'taskkill /F /PID {old_pid}', shell=True, capture_output=True, timeout=5)
                    logger.info(f"  已释放端口 {port} (PID={old_pid})")
            time.sleep(2)
    except Exception as e:
        logger.warning(f"释放前端端口失败: {e}")

    try:
        # 隐藏窗口启动
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # DETACHED_PROCESS = 0x00000008, CREATE_NEW_PROCESS_GROUP = 0x00000200, CREATE_NO_WINDOW = 0x08000000
        creationflags = 0x00000008 | 0x00000200 | 0x08000000

        cmd = [start_cmd] + start_args
        proc = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            startupinfo=startupinfo,
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True
        )

        new_pid = proc.pid
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(new_pid), encoding='utf-8')
        logger.info(f"前端已启动，新PID={new_pid}，等待 {wait_seconds} 秒后健康检查...")

        # 等待前端完全启动
        time.sleep(wait_seconds)

        # 再次健康检查
        alive, detail = check_frontend_alive(config)
        if alive:
            logger.info(f"前端重启成功，健康检查通过")
            return True, new_pid, "前端重启成功"
        else:
            return False, new_pid, f"前端重启后健康检查仍失败: {detail}"

    except Exception as e:
        return False, None, f"重启前端异常: {e}"


# ============================================================
# 调度器状态探测
# ============================================================
def check_scheduler_status(config):
    """
    检查调度器状态
    返回: (调度器在运行: bool, 任务数量: int, 详情: str)
    """
    backend_cfg = config["后端"]
    host = backend_cfg["主机"]
    port = backend_cfg["端口"]
    timeout = backend_cfg["请求超时秒"]
    api_path = config["调度器"]["状态API"]

    try:
        url = f"http://{host}:{port}{api_path}"
        resp = requests.get(url, timeout=timeout)
        if resp.status_code != 200:
            return False, 0, f"调度器状态API返回 {resp.status_code}"
        data = resp.json()
        if not data.get("success"):
            return False, 0, f"调度器状态API返回失败: {data}"
        # 实际API返回格式：{"success": true, "scheduler_running": true, "jobs_count": 13, "jobs": [...]}
        # 兼容两种字段名（scheduler_running/running, jobs_count/任务数量）
        running = data.get("scheduler_running", data.get("running", False))
        task_count = data.get("jobs_count", data.get("任务数量", 0))
        if running and task_count > 0:
            return True, task_count, f"调度器运行中，任务数 {task_count}"
        else:
            return False, task_count, f"调度器未运行或无任务（running={running}, 任务数={task_count}）"
    except requests.exceptions.Timeout:
        return False, 0, "调度器状态API超时"
    except Exception as e:
        return False, 0, f"调度器状态API异常: {e}"


# ============================================================
# 备份状态探测
# ============================================================
def read_backup_status(config):
    """
    直读备份状态JSON文件（不依赖后端API）
    返回: dict 或 None
    """
    status_file = Path(config["备份"]["状态文件"])
    if not status_file.exists():
        logger.warning(f"备份状态文件不存在: {status_file}")
        return None
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取备份状态文件异常: {e}")
        return None


def check_backup_freshness(config, status):
    """
    检查备份时效性
    返回: (正常: bool, 详情: str)
    """
    if not status:
        return False, "无法读取备份状态文件"

    last_backup_time_str = status.get("last_backup_time")
    if not last_backup_time_str:
        return False, "无备份记录（last_backup_time 为空）"

    try:
        last_backup_time = datetime.fromisoformat(last_backup_time_str)
    except Exception:
        try:
            # 兼容多种时间格式
            last_backup_time = datetime.strptime(last_backup_time_str, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            return False, f"备份时间格式无法解析: {last_backup_time_str} ({e})"

    now = datetime.now()
    hours_ago = (now - last_backup_time).total_seconds() / 3600
    threshold_hours = config["备份"]["超时阈值小时"]

    if hours_ago > threshold_hours:
        return False, f"备份超时（{hours_ago:.1f}小时前 > 阈值{threshold_hours}小时）"

    return True, f"备份时效正常（{hours_ago:.1f}小时前）"


def trigger_backup(config):
    """
    触发补偿备份（调用后端API）
    返回: (成功: bool, 详情: str)
    """
    api_url = config["备份"]["触发备份API"]
    timeout = config["后端"]["请求超时秒"]
    try:
        logger.info(f"触发补偿备份，调用 API: {api_url}")
        resp = requests.post(api_url, timeout=60)  # 备份可能较慢，给60秒
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return True, f"补偿备份触发成功: {data.get('data', {}).get('filename', '未知')}"
            else:
                return False, f"补偿备份API返回失败: {data}"
        else:
            return False, f"补偿备份API HTTP {resp.status_code}"
    except Exception as e:
        return False, f"触发补偿备份异常: {e}"


# ============================================================
# 磁盘空间预警 + 旧备份清理
# ============================================================
def check_disk_space(config):
    """
    检查磁盘空间，根据阈值发出不同等级预警
    返回: [(路径, 等级, 剩余GB, 详情), ...]
    """
    if "磁盘空间预警" not in config:
        return []
    disk_cfg = config["磁盘空间预警"]
    if not disk_cfg.get("启用", True):
        return []

    check_paths = disk_cfg.get("检查路径", ["D:\\"])
    red_gb = disk_cfg.get("红色告警阈值GB", 5)
    yellow_gb = disk_cfg.get("黄色预警阈值GB", 30)
    blue_gb = disk_cfg.get("蓝色提示阈值GB", 80)

    results = []
    for path in check_paths:
        try:
            usage = shutil.disk_usage(path)
            free_gb = usage.free / (1024 ** 3)
            total_gb = usage.total / (1024 ** 3)

            if free_gb < red_gb:
                level = "red"
                detail = f"磁盘空间严重不足（剩余 {free_gb:.1f}GB < {red_gb}GB）"
            elif free_gb < yellow_gb:
                level = "yellow"
                detail = f"磁盘空间不足（剩余 {free_gb:.1f}GB < {yellow_gb}GB），建议清理旧备份"
            elif free_gb < blue_gb:
                level = "blue"
                detail = f"磁盘空间偏低（剩余 {free_gb:.1f}GB < {blue_gb}GB）"
            else:
                level = "ok"
                detail = f"磁盘空间充足（剩余 {free_gb:.1f}GB / 总 {total_gb:.1f}GB）"

            results.append((path, level, free_gb, detail))
            logger.info(f"  磁盘 {path}: {detail}")
        except Exception as e:
            logger.error(f"  磁盘空间检查失败 {path}: {e}")
            results.append((path, "error", 0, f"检查失败: {e}"))

    return results


def cleanup_old_backups(config):
    """
    清理旧备份文件（保留最近N个，清理更老的）
    返回: (清理的文件数, 详情)
    """
    if "磁盘空间预警" not in config:
        return 0, "未配置磁盘预警"
    disk_cfg = config["磁盘空间预警"]
    backup_dirs = disk_cfg.get("备份保留目录", [])
    keep_count = 7  # 保留最近7个备份

    total_cleaned = 0
    details = []

    for backup_dir in backup_dirs:
        backup_path = Path(backup_dir)
        if not backup_path.exists():
            continue

        try:
            # 列出所有.sql备份文件，按修改时间排序
            sql_files = sorted(
                backup_path.glob("*.sql"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )

            # 删除超出保留数量的旧文件
            cleaned = 0
            for old_file in sql_files[keep_count:]:
                try:
                    file_size_mb = old_file.stat().st_size / (1024 * 1024)
                    old_file.unlink()
                    cleaned += 1
                    logger.info(f"    删除旧备份: {old_file.name} ({file_size_mb:.1f}MB)")
                except Exception as e:
                    logger.warning(f"    删除失败 {old_file.name}: {e}")

            if cleaned > 0:
                total_cleaned += cleaned
                details.append(f"{backup_dir}: 清理{cleaned}个")
        except Exception as e:
            logger.warning(f"  清理目录失败 {backup_dir}: {e}")

    return total_cleaned, "；".join(details) if details else "无旧备份需清理"


def should_disk_alert(level, config):
    """
    判断磁盘空间是否应该发送告警（避免24小时内重复预警）
    """
    if "磁盘空间预警" not in config:
        return False
    silence_hours = config["磁盘空间预警"].get("预警间隔小时", 24)
    silence_seconds = silence_hours * 3600

    state = _load_alert_state()
    alert_key = f"disk_space_{level}"
    last_alert = state.get(alert_key)
    if last_alert:
        try:
            last_time = datetime.fromisoformat(last_alert)
            if (datetime.now() - last_time).total_seconds() < silence_seconds:
                return False
        except Exception:
            pass

    state[alert_key] = datetime.now().isoformat()
    _save_alert_state(state)
    return True


# ============================================================
# 备份失败原因分析 + 自愈动作
# ============================================================
def analyze_backup_failure(backup_status):
    """
    分析备份失败原因
    返回: [(失败原因类型, 失败详情), ...]
    """
    if not backup_status:
        return []

    results = backup_status.get("backup_results", [])
    failures = []

    for r in results:
        if not r.get("success") and not r.get("skipped"):
            error_msg = r.get("error", "")
            label = r.get("label", "未知位置")

            # 分类失败原因
            if "权限" in error_msg or "Permission" in error_msg:
                failures.append(("权限不足", f"[{label}] {error_msg}"))
            elif "空间" in error_msg or "No space" in error_msg or "磁盘" in error_msg:
                failures.append(("磁盘空间不足", f"[{label}] {error_msg}"))
            elif "connection" in error_msg.lower() or "连接" in error_msg or "refused" in error_msg.lower():
                failures.append(("数据库连接失败", f"[{label}] {error_msg}"))
            elif "超时" in error_msg or "timeout" in error_msg.lower() or "Timeout" in error_msg:
                failures.append(("pg_dump超时", f"[{label}] {error_msg}"))
            else:
                failures.append(("其他错误", f"[{label}] {error_msg}"))

    return failures


def perform_self_healing(failure_type, config):
    """
    根据失败原因执行自愈动作
    返回: (成功: bool, 详情: str)
    """
    heal_cfg = config.get("失败原因自愈", {})
    if not heal_cfg.get("启用", True):
        return False, "自愈功能未启用"

    if failure_type == "权限不足":
        if not heal_cfg.get("权限不足", {}).get("启用", True):
            return False, "权限不足自愈未启用"
        # 修复备份目录权限（授予当前用户完全控制）
        backup_dirs = config.get("磁盘空间预警", {}).get("备份保留目录", [])
        user = os.environ.get("USERNAME", "")
        fixed = []
        for dir_path in backup_dirs:
            try:
                subprocess.run(
                    f'icacls "{dir_path}" /grant:r {user}:(OI)(CI)F /T',
                    shell=True, capture_output=True, timeout=30
                )
                fixed.append(dir_path)
                logger.info(f"  权限修复: {dir_path}")
            except Exception as e:
                logger.warning(f"  权限修复失败 {dir_path}: {e}")
        return True, f"已修复目录权限: {fixed}"

    elif failure_type == "磁盘空间不足":
        if not heal_cfg.get("磁盘空间不足", {}).get("启用", True):
            return False, "磁盘清理自愈未启用"
        cleaned_count, detail = cleanup_old_backups(config)
        if cleaned_count > 0:
            return True, f"已清理{cleaned_count}个旧备份 ({detail})"
        else:
            return False, "无旧备份可清理，需人工扩容"

    elif failure_type == "数据库连接失败":
        if not heal_cfg.get("数据库连接失败", {}).get("启用", True):
            return False, "数据库重启自愈未启用"
        # 重启PostgreSQL服务
        try:
            logger.info("  尝试重启 PostgreSQL 服务...")
            result = subprocess.run(
                'net stop postgresql-x64-17 && timeout /t 3 /nobreak >nul && net start postgresql-x64-17',
                shell=True, capture_output=True, text=True, timeout=60
            )
            if "成功" in result.stdout or "success" in result.stdout.lower():
                return True, "PostgreSQL服务已重启"
            else:
                return False, f"PostgreSQL重启失败: {result.stdout[:200]}"
        except Exception as e:
            return False, f"PostgreSQL重启异常: {e}"

    elif failure_type == "pg_dump超时":
        if not heal_cfg.get("pg_dump超时", {}).get("启用", True):
            return False, "超时自愈未启用"
        # 超时无法直接修复，建议人工介入
        return False, "pg_dump超时，建议检查数据库负载后手动重试"

    return False, f"未知失败类型: {failure_type}"


# ============================================================
# 飞书推送有效性检查
# ============================================================
def check_feishu_notification(status):
    """
    检查飞书推送是否成功（从备份状态文件读取）
    返回: (推送成功: bool, 详情: str)
    """
    if not status:
        return True, "无法读取备份状态，跳过推送检查"  # 不作为故障

    last_notif = status.get("last_notification")
    if not last_notif:
        return True, "无推送记录，跳过推送检查"

    success = last_notif.get("success")
    if success:
        return True, "飞书推送正常"
    else:
        error = last_notif.get("error", "未知错误")
        return False, f"飞书推送失败: {error}"


# ============================================================
# 独立飞书告警通道（不依赖后端，读 feishu_config.json 用应用API）
# ============================================================
def _get_feishu_access_token(feishu_cfg):
    """
    获取飞书应用API的access_token
    返回: (token: str|None, 错误信息: str)
    """
    app_id = feishu_cfg.get("App ID", "").strip()
    app_secret = feishu_cfg.get("App Secret", "").strip()
    if not app_id or not app_secret:
        return None, "App ID 或 App Secret 为空"

    try:
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        body = {"app_id": app_id, "app_secret": app_secret}
        resp = requests.post(url, json=body, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return data.get("app_access_token"), ""
        else:
            return None, f"获取token失败: code={data.get('code')}, msg={data.get('msg')}"
    except Exception as e:
        return None, f"获取token异常: {e}"


def _send_feishu_app_message(feishu_cfg, message, severity):
    """
    通过飞书应用API发送群消息
    返回: (成功: bool, 错误信息: str)
    """
    chat_id = feishu_cfg.get("群聊ID", "").strip()
    if not chat_id:
        return False, "群聊ID为空"

    token, err = _get_feishu_access_token(feishu_cfg)
    if not token:
        return False, f"获取access_token失败: {err}"

    full_msg = f"【ERP监督告警】\n时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n等级：{severity}\n────────\n{message}\n────────\n—— ERP监督脚本"

    try:
        url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        headers = {"Authorization": f"Bearer {token}"}
        body = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": full_msg}, ensure_ascii=False)
        }
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return True, ""
        else:
            return False, f"发送失败: code={data.get('code')}, msg={data.get('msg')}"
    except Exception as e:
        return False, f"发送异常: {e}"


def send_alert(config, message, severity="normal"):
    """
    通过独立飞书应用API发送告警（不依赖后端服务）
    - 直接读 feishu_config.json
    - 自己获取access_token并发送群消息
    - 失败时降级写本地告警文件
    返回: True=发送成功或已降级, False=完全失败
    """
    feishu_cfg_path = config.get("独立飞书通道", {}).get("配置文件", "")
    retry_count = config.get("独立飞书通道", {}).get("重试次数", 3)
    retry_interval = config.get("独立飞书通道", {}).get("重试间隔秒", 5)

    # 时间戳+完整消息
    full_msg = f"【ERP监督告警】\n时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n等级：{severity}\n────────\n{message}\n────────\n—— ERP监督脚本"

    # 读取飞书配置
    if not feishu_cfg_path or not Path(feishu_cfg_path).exists():
        logger.warning(f"飞书配置文件不存在: {feishu_cfg_path}，降级为本地告警文件")
        try:
            with open(ALERT_FALLBACK_FILE, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n{full_msg}\n")
            logger.info(f"本地告警已写入: {ALERT_FALLBACK_FILE}")
            return True
        except Exception as e:
            logger.error(f"写本地告警文件失败: {e}")
            return False

    try:
        with open(feishu_cfg_path, 'r', encoding='utf-8') as f:
            feishu_cfg = json.load(f)
    except Exception as e:
        logger.error(f"读取飞书配置失败: {e}，降级为本地告警文件")
        try:
            with open(ALERT_FALLBACK_FILE, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n{full_msg}\n")
            return True
        except:
            return False

    # 重试发送
    for attempt in range(1, retry_count + 1):
        success, err = _send_feishu_app_message(feishu_cfg, message, severity)
        if success:
            logger.info(f"飞书告警发送成功（第{attempt}次尝试）")
            return True
        else:
            logger.warning(f"飞书告警第{attempt}次失败: {err}")
            if attempt < retry_count:
                time.sleep(retry_interval)

    # 所有重试失败，降级写本地告警文件
    logger.error(f"飞书API连续{retry_count}次失败，降级为本地告警文件")
    try:
        with open(ALERT_FALLBACK_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n[飞书API发送失败，降级写入]\n{full_msg}\n")
        return True
    except Exception as e:
        logger.error(f"写本地告警文件也失败: {e}")
        return False


# ============================================================
# 告警静默期管理
# ============================================================
def _load_alert_state():
    """加载告警静默状态"""
    if not ALERT_STATE_FILE.exists():
        return {}
    try:
        with open(ALERT_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save_alert_state(state):
    """保存告警静默状态"""
    try:
        with open(ALERT_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"保存告警静默状态失败: {e}")


def should_alert(alert_type, config):
    """
    判断是否应该发送告警（避免30分钟内重复告警同一故障）
    返回: True=应该告警, False=在静默期内
    """
    silence_seconds = config["监督自身"].get("告警静默期秒", 1800)
    state = _load_alert_state()
    now = datetime.now()

    last_alert = state.get(alert_type)
    if last_alert:
        try:
            last_time = datetime.fromisoformat(last_alert)
            if (now - last_time).total_seconds() < silence_seconds:
                logger.info(f"告警 {alert_type} 在静默期内（上次告警: {last_alert}），跳过")
                return False
        except Exception:
            pass

    # 更新告警时间
    state[alert_type] = now.isoformat()
    _save_alert_state(state)
    return True


def clear_alert_state(alert_type):
    """故障恢复后清理告警状态，以便下次故障能立即告警"""
    state = _load_alert_state()
    if alert_type in state:
        del state[alert_type]
        _save_alert_state(state)
        logger.info(f"告警状态已清除: {alert_type}")


# ============================================================
# 主监督流程
# ============================================================
def run_supervisor():
    """监督脚本主入口"""
    logger.info("=" * 60)
    logger.info("ERP系统监督脚本启动")
    logger.info("=" * 60)

    # 1. 加载配置
    config = load_config()
    max_run_seconds = config["监督自身"].get("单次最大运行秒", 120)
    start_time = time.time()

    # 2. 获取PID锁
    lock_file = config["监督自身"].get("PID锁文件", "state/supervisor.pid")
    if not acquire_supervisor_lock(lock_file):
        return  # 已有实例在运行，退出

    try:
        # ============================================================
        # 探测1：后端存活
        # ============================================================
        logger.info("[探测1] 后端存活检测...")
        backend_alive, detail = check_backend_alive(config)
        if backend_alive:
            logger.info(f"  ✅ 后端存活正常")
            clear_alert_state("backend_down")
        else:
            logger.error(f"  ❌ 后端故障: {detail}")
            # 自愈：重启后端
            if should_alert("backend_down", config):
                logger.info("  🔄 尝试自愈：重启后端...")
                success, new_pid, restart_detail = restart_backend(config)
                if success:
                    logger.info(f"  ✅ 后端自愈成功: {restart_detail}")
                    send_alert(config, f"后端故障自愈成功\n故障: {detail}\n自愈: {restart_detail}", "normal")
                    clear_alert_state("backend_down")
                else:
                    logger.error(f"  ❌ 后端自愈失败: {restart_detail}")
                    send_alert(config, f"后端故障且自愈失败\n故障: {detail}\n自愈: {restart_detail}", "critical")
                    # 后端挂了，后续探测无法进行
                    return

        # ============================================================
        # 探测2：前端存活（新增，保证前端可访问）
        # ============================================================
        logger.info("[探测2] 前端存活检测...")
        frontend_alive, fe_detail = check_frontend_alive(config)
        if frontend_alive:
            logger.info(f"  ✅ {fe_detail}")
            clear_alert_state("frontend_down")
        else:
            logger.error(f"  ❌ 前端故障: {fe_detail}")
            if should_alert("frontend_down", config):
                logger.info("  🔄 尝试自愈：重启前端...")
                fe_success, fe_pid, fe_restart_detail = restart_frontend(config)
                if fe_success:
                    logger.info(f"  ✅ 前端自愈成功: {fe_restart_detail}")
                    send_alert(config, f"前端故障自愈成功\n故障: {fe_detail}\n自愈: {fe_restart_detail}", "normal")
                    clear_alert_state("frontend_down")
                else:
                    logger.error(f"  ❌ 前端自愈失败: {fe_restart_detail}")
                    send_alert(config, f"前端故障且自愈失败\n故障: {fe_detail}\n自愈: {fe_restart_detail}", "critical")

        # ============================================================
        # 探测3：调度器状态
        # ============================================================
        logger.info("[探测3] 调度器状态检测...")
        if not backend_alive:
            logger.info("  ⏭️ 后端刚重启，跳过调度器状态检查")
        else:
            sched_running, task_count, sched_detail = check_scheduler_status(config)
            if sched_running:
                logger.info(f"  ✅ {sched_detail}")
                clear_alert_state("scheduler_down")
            else:
                logger.error(f"  ❌ 调度器异常: {sched_detail}")
                if should_alert("scheduler_down", config):
                    logger.info("  🔄 尝试自愈：重启后端以间接重启调度器...")
                    success, new_pid, restart_detail = restart_backend(config)
                    if success:
                        logger.info(f"  ✅ 调度器自愈成功（后端重启）: {restart_detail}")
                        send_alert(config, f"调度器异常自愈成功\n故障: {sched_detail}\n自愈: 后端重启（新PID={new_pid}）", "normal")
                        clear_alert_state("scheduler_down")
                        backend_alive = True
                    else:
                        logger.error(f"  ❌ 调度器自愈失败: {restart_detail}")
                        send_alert(config, f"调度器异常且自愈失败\n故障: {sched_detail}\n自愈: {restart_detail}", "critical")
                        return

        # ============================================================
        # 探测4：磁盘空间预警（新增，提前发现空间不足）
        # ============================================================
        logger.info("[探测4] 磁盘空间检测...")
        disk_results = check_disk_space(config)
        for path, level, free_gb, detail in disk_results:
            if level == "ok":
                continue
            elif level == "red":
                logger.error(f"  ❌ {detail}")
                if should_disk_alert("red", config):
                    # 尝试清理旧备份
                    cleaned, clean_detail = cleanup_old_backups(config)
                    if cleaned > 0:
                        logger.info(f"  🔄 自愈：已清理{cleaned}个旧备份 ({clean_detail})")
                        send_alert(config, f"磁盘空间严重不足（{path} 剩余 {free_gb:.1f}GB）\n自愈: {clean_detail}", "critical")
                    else:
                        send_alert(config, f"磁盘空间严重不足（{path} 剩余 {free_gb:.1f}GB）\n无旧备份可清理，需立即扩容！", "critical")
            elif level == "yellow":
                logger.warning(f"  ⚠️ {detail}")
                if should_disk_alert("yellow", config):
                    send_alert(config, f"磁盘空间不足预警（{path} 剩余 {free_gb:.1f}GB）\n建议清理旧备份或扩容", "normal")
            elif level == "blue":
                logger.info(f"  ℹ️ {detail}")
                if should_disk_alert("blue", config):
                    send_alert(config, f"磁盘空间偏低提示（{path} 剩余 {free_gb:.1f}GB）", "normal")

        # ============================================================
        # 探测5：备份时效
        # ============================================================
        logger.info("[探测5] 备份时效检测...")
        backup_status = read_backup_status(config)
        backup_ok, backup_detail = check_backup_freshness(config, backup_status)
        if backup_ok:
            logger.info(f"  ✅ {backup_detail}")
            clear_alert_state("backup_stale")
        else:
            logger.error(f"  ❌ {backup_detail}")
            if should_alert("backup_stale", config):
                alive_now, _ = check_backend_alive(config)
                if not alive_now:
                    logger.error("  ❌ 后端不存活，无法触发补偿备份")
                    send_alert(config, f"备份时效异常\n故障: {backup_detail}\n无法触发补偿备份：后端不存活", "critical")
                else:
                    logger.info("  🔄 尝试自愈：触发补偿备份...")
                    backup_success, backup_msg = trigger_backup(config)
                    if backup_success:
                        logger.info(f"  ✅ 补偿备份成功: {backup_msg}")
                        send_alert(config, f"备份超时自愈成功\n故障: {backup_detail}\n自愈: {backup_msg}", "normal")
                        clear_alert_state("backup_stale")
                    else:
                        logger.error(f"  ❌ 补偿备份失败: {backup_msg}")
                        send_alert(config, f"备份超时且自愈失败\n故障: {backup_detail}\n自愈: {backup_msg}", "critical")

        # ============================================================
        # 探测6：连续失败次数 + 失败原因分析+自愈（新增原因分析）
        # ============================================================
        logger.info("[探测6] 备份失败原因分析...")
        if backup_status:
            consecutive_failures = backup_status.get("consecutive_failures", 0)
            threshold = config["备份"]["连续失败告警阈值"]
            if consecutive_failures >= threshold:
                logger.error(f"  ❌ 备份连续失败 {consecutive_failures} 次（阈值 {threshold}）")
                # 分析失败原因
                failures = analyze_backup_failure(backup_status)
                if failures:
                    failure_summary = "\n".join([f"- {ft}: {fd}" for ft, fd in failures])
                    logger.error(f"  失败原因:\n{failure_summary}")

                    if should_alert("backup_failures", config):
                        # 尝试自愈（取第一个失败原因）
                        first_failure_type = failures[0][0]
                        logger.info(f"  🔄 尝试自愈：{first_failure_type}...")
                        heal_success, heal_detail = perform_self_healing(first_failure_type, config)
                        if heal_success:
                            logger.info(f"  ✅ 自愈成功: {heal_detail}")
                            # 自愈后重试备份
                            alive_now, _ = check_backend_alive(config)
                            if alive_now:
                                logger.info("  🔄 自愈后重试备份...")
                                retry_success, retry_msg = trigger_backup(config)
                                if retry_success:
                                    send_alert(config, f"备份失败自愈成功\n失败原因:\n{failure_summary}\n自愈: {heal_detail}\n重试备份: {retry_msg}", "normal")
                                    clear_alert_state("backup_failures")
                                else:
                                    send_alert(config, f"备份失败自愈成功但重试备份失败\n失败原因:\n{failure_summary}\n自愈: {heal_detail}\n重试: {retry_msg}", "critical")
                            else:
                                send_alert(config, f"备份失败自愈成功但后端不存活\n失败原因:\n{failure_summary}\n自愈: {heal_detail}", "critical")
                        else:
                            logger.error(f"  ❌ 自愈失败: {heal_detail}")
                            send_alert(config, f"备份连续失败且自愈失败\n连续失败: {consecutive_failures}次\n失败原因:\n{failure_summary}\n自愈: {heal_detail}\n请立即人工介入！", "critical")
                else:
                    if should_alert("backup_failures", config):
                        send_alert(config, f"备份连续失败 {consecutive_failures} 次\n无具体失败原因，请检查日志", "critical")
            else:
                logger.info(f"  ✅ 连续失败次数 {consecutive_failures}（阈值 {threshold}）")
                clear_alert_state("backup_failures")

        # ============================================================
        # 探测7：飞书推送有效性
        # ============================================================
        logger.info("[探测7] 飞书推送有效性检测...")
        notif_ok, notif_detail = check_feishu_notification(backup_status)
        if notif_ok:
            logger.info(f"  ✅ {notif_detail}")
            clear_alert_state("notification_failed")
        else:
            logger.error(f"  ❌ {notif_detail}")
            if should_alert("notification_failed", config):
                send_alert(
                    config,
                    f"飞书推送通道异常\n故障: {notif_detail}\n请检查 feishu_config.json 和飞书应用配置",
                    "critical"
                )

        # ============================================================
        # 总结
        # ============================================================
        elapsed = time.time() - start_time
        logger.info(f"监督流程完成，耗时 {elapsed:.1f} 秒")
        logger.info("=" * 60)

    except Exception as e:
        logger.exception(f"监督脚本异常: {e}")
        try:
            send_alert(config, f"监督脚本异常\n错误: {str(e)}", "critical")
        except Exception:
            pass
    finally:
        release_supervisor_lock(lock_file)


def run_daemon(interval_seconds=1800):
    """常驻进程模式（不依赖外部调度器）

    每 interval_seconds 秒执行一次 run_supervisor()，永不退出。
    所有异常都被捕获并记录，确保进程持续运行。
    由 start_servers.py 启动和管理，如果本进程崩溃会被 start_servers.py 重启。
    """
    logger.info("=" * 60)
    logger.info(f"ERP监督脚本进入常驻进程模式，循环间隔 {interval_seconds} 秒（{interval_seconds//60} 分钟）")
    logger.info("=" * 60)

    # 写入守护进程PID（供 start_servers.py 监控）
    daemon_pid_file = STATE_DIR / "supervisor_daemon.pid"
    try:
        daemon_pid_file.write_text(str(os.getpid()), encoding='utf-8')
    except Exception:
        pass

    consecutive_errors = 0
    max_consecutive_errors = 10  # 连续10次错误后等待更长时间

    while True:
        try:
            run_supervisor()
            consecutive_errors = 0  # 成功执行，重置错误计数
        except Exception as e:
            consecutive_errors += 1
            logger.exception(f"监督流程异常（连续第{consecutive_errors}次）: {e}")
            error_log = LOG_DIR / "startup_error.log"
            try:
                with open(error_log, 'a', encoding='utf-8') as f:
                    import traceback
                    f.write(f"\n{'='*60}\n")
                    f.write(f"[{datetime.now()}] 监督流程异常（连续第{consecutive_errors}次）\n")
                    f.write(f"错误: {e}\n")
                    f.write(f"堆栈:\n{traceback.format_exc()}\n")
            except Exception:
                pass
            if consecutive_errors >= max_consecutive_errors:
                logger.error(f"连续错误 {consecutive_errors} 次，等待 5 分钟后重试...")
                time.sleep(300)
                consecutive_errors = 0

        logger.info(f"等待 {interval_seconds} 秒后进入下一轮监督...")
        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("收到终止信号，监督进程退出")
            break


if __name__ == "__main__":
    # 支持两种运行模式：
    # 1. 常驻进程模式：python supervisor.py --daemon [间隔秒数]
    #    由 start_servers.py 启动，不依赖外部调度器（Windows/Linux 通用）
    # 2. 单次运行模式：python supervisor.py
    #    被 Windows 任务计划程序或 cron 调用（兼容旧方式）

    args = sys.argv[1:]
    is_daemon = "--daemon" in args

    if is_daemon:
        # 常驻进程模式
        interval = 1800  # 默认30分钟
        for arg in args:
            if arg.isdigit():
                interval = int(arg)
                break
        run_daemon(interval_seconds=interval)
    else:
        # 单次运行模式（兼容旧方式）
        try:
            run_supervisor()
        except Exception as e:
            error_log = LOG_DIR / "startup_error.log"
            try:
                with open(error_log, 'a', encoding='utf-8') as f:
                    import traceback
                    f.write(f"\n{'='*60}\n")
                    f.write(f"[{datetime.now()}] 监督脚本启动失败\n")
                    f.write(f"错误: {e}\n")
                    f.write(f"堆栈:\n{traceback.format_exc()}\n")
            except Exception:
                pass
            sys.exit(1)
