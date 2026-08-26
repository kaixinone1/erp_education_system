"""
数据库自动备份服务
- 每天定时备份（pg_dump）
- 一式三份，备份到三个独立位置
- 支持 Git 仓库备份 + 自动推送到远程仓库
- 备份失败时记录状态，供前端弹窗提示
"""
import subprocess
import os
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
BACKUP_CONFIG_FILE = os.path.join(CONFIG_DIR, 'db_backup_config.json')
STATUS_FILE = os.path.join(CONFIG_DIR, 'db_backup_status.json')

DB_NAME = "taiping_education"
DB_USER = "taiping_user"
DB_PASSWORD = "taiping_password"
DB_HOST = "localhost"
DB_PORT = "5432"

# 默认备份路径（三个）
DEFAULT_BACKUP_PATHS = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "备份", "数据库自动备份"),
    "",  # 待用户配置
    "",  # 待用户配置
]

# 默认 Git 备份配置
DEFAULT_GIT_CONFIG = {
    "enabled": False,
    "remote_name": "origin",
    "branch": "main",
    "backup_subdir": "数据库备份",  # 仓库内子目录
}


def get_project_root():
    """自动检测项目根目录（Git仓库根目录）"""
    # 从当前文件向上查找 .git 目录
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # 回退：使用项目结构推算（db_backup_service.py → services → backend → tp_education_system → 项目根）
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_git_remote_url(repo_path=None):
    """自动获取Git远程仓库URL"""
    if repo_path is None:
        repo_path = get_project_root()
    git_exe = find_git()
    if not git_exe:
        return None
    try:
        result = subprocess.run(
            [git_exe, "remote", "get-url", "origin"],
            cwd=repo_path, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None


def get_git_branch(repo_path=None):
    """自动获取当前Git分支"""
    if repo_path is None:
        repo_path = get_project_root()
    git_exe = find_git()
    if not git_exe:
        return "main"
    try:
        result = subprocess.run(
            [git_exe, "branch", "--show-current"],
            cwd=repo_path, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "main"


def get_config():
    """读取备份配置"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(BACKUP_CONFIG_FILE):
        with open(BACKUP_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 兼容旧配置：没有 git_config 时补充默认值
            if "git_config" not in config:
                config["git_config"] = DEFAULT_GIT_CONFIG
            return config
    return {
        "backup_paths": DEFAULT_BACKUP_PATHS,
        "backup_time": "01:00",
        "keep_days": 30,
        "enabled": True,
        "git_config": DEFAULT_GIT_CONFIG,
    }


def save_config(config):
    """保存备份配置"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(BACKUP_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_status():
    """读取备份状态"""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_backup_time": None,
        "last_backup_success": None,
        "backup_results": [],
        "failed_paths": [],
        "consecutive_failures": 0,
    }


def save_status(status):
    """保存备份状态"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def find_pg_dump():
    """查找 pg_dump.exe 路径"""
    possible_paths = [
        r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\13\bin\pg_dump.exe",
    ]
    
    for p in possible_paths:
        if os.path.exists(p):
            return p
    
    try:
        result = subprocess.run(
            ["where", "pg_dump"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None


def find_git():
    """查找 git.exe 路径"""
    possible_paths = [
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    try:
        result = subprocess.run(["where", "git"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    return None


def git_backup(temp_file, filename, git_config):
    """
    将备份文件提交到 Git 仓库并推送到远程
    自动检测项目Git仓库路径，无需手动配置
    返回: {"success": bool, "message": str}
    """
    if not git_config.get("enabled"):
        return {"success": True, "message": "Git备份未启用", "skipped": True}
    
    # 自动检测项目Git仓库路径（无需用户手动配置）
    repo_path = get_project_root()
    if not repo_path or not os.path.isdir(os.path.join(repo_path, ".git")):
        return {"success": False, "message": "当前项目不是Git仓库，无法进行Git备份", "skipped": True}
    
    git_exe = find_git()
    if not git_exe:
        return {"success": False, "message": "找不到git.exe"}
    
    backup_subdir = git_config.get("backup_subdir", "数据库备份")
    remote_name = git_config.get("remote_name", "origin")
    branch = git_config.get("branch", "main")
    
    try:
        # 确保备份子目录存在
        dest_dir = os.path.join(repo_path, backup_subdir)
        os.makedirs(dest_dir, exist_ok=True)
        
        dest_file = os.path.join(dest_dir, filename)
        shutil.copy2(temp_file, dest_file)
        
        # git add
        result = subprocess.run(
            [git_exe, "add", os.path.join(backup_subdir, filename)],
            cwd=repo_path, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"success": False, "message": f"git add 失败: {result.stderr.strip()}"}
        
        # git commit
        commit_msg = f"数据库自动备份 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(
            [git_exe, "commit", "-m", commit_msg],
            cwd=repo_path, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            # "nothing to commit" 也算成功
            if "nothing to commit" in result.stdout.lower() or "nothing to commit" in result.stderr.lower():
                logger.info("Git备份: 无变更，跳过提交")
            else:
                return {"success": False, "message": f"git commit 失败: {result.stderr.strip()}"}
        
        # git push
        result = subprocess.run(
            [git_exe, "push", remote_name, branch],
            cwd=repo_path, capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return {"success": False, "message": f"git push 失败: {result.stderr.strip()}"}
        
        logger.info(f"Git备份成功: {dest_file} → {remote_name}/{branch}")
        return {"success": True, "message": f"已推送至 {remote_name}/{branch}", "file": dest_file}
        
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Git操作超时"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def verify_git_repo(repo_path=None):
    """验证路径是否为有效的 Git 仓库（不传路径则自动检测项目仓库）"""
    if repo_path is None:
        repo_path = get_project_root()
    git_exe = find_git()
    if not git_exe:
        return {"success": False, "message": "找不到git.exe"}
    if not repo_path or not os.path.exists(repo_path):
        return {"success": False, "message": "仓库路径不存在"}
    try:
        result = subprocess.run(
            [git_exe, "rev-parse", "--git-dir"],
            cwd=repo_path, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            # 获取远程仓库信息
            remote_result = subprocess.run(
                [git_exe, "remote", "-v"],
                cwd=repo_path, capture_output=True, text=True, timeout=10
            )
            remotes = {}
            for line in remote_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        remotes[parts[0]] = parts[1]
            
            branch_result = subprocess.run(
                [git_exe, "branch", "--show-current"],
                cwd=repo_path, capture_output=True, text=True, timeout=10
            )
            current_branch = branch_result.stdout.strip()
            
            return {
                "success": True,
                "message": "有效的Git仓库",
                "repo_path": repo_path,
                "remotes": remotes,
                "current_branch": current_branch,
            }
        else:
            return {"success": False, "message": "不是有效的Git仓库"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def run_backup() -> dict:
    """
    执行数据库备份（一式三份 + Git）
    返回: {"success": bool, "results": [...], "failed_paths": [...]}
    """
    config = get_config()
    status = get_status()
    
    if not config.get("enabled", True):
        logger.info("数据库自动备份已禁用，跳过")
        return {"success": True, "results": [], "failed_paths": [], "skipped": True}
    
    pg_dump = find_pg_dump()
    if not pg_dump:
        logger.error("找不到 pg_dump.exe，备份失败")
        return {"success": False, "error": "找不到pg_dump.exe", "results": [], "failed_paths": []}
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"taiping_education_{timestamp}.sql"
    
    results = []
    failed_paths = []
    backup_paths = config.get("backup_paths", DEFAULT_BACKUP_PATHS)
    
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_backup")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, filename)
    
    try:
        # 执行 pg_dump
        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD
        
        cmd = [
            pg_dump,
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-F", "p",
            "-f", temp_file,
            DB_NAME
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            env=env
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() or "pg_dump执行失败"
            logger.error(f"pg_dump 失败: {error_msg}")
            update_status(status, False, failed_paths=backup_paths)
            return {"success": False, "error": error_msg, "results": [], "failed_paths": backup_paths}
        
        file_size = os.path.getsize(temp_file)
        if file_size < 1024:
            logger.warning(f"备份文件过小 ({file_size} bytes)，可能备份不完整")
        
        # 备份到三个文件位置
        for i, backup_path in enumerate(backup_paths):
            path_label = f"位置{i+1}"
            if not backup_path or not backup_path.strip():
                results.append({
                    "path": backup_path,
                    "label": path_label,
                    "success": False,
                    "error": "未配置备份路径",
                    "skipped": True,
                })
                continue
            
            try:
                os.makedirs(backup_path, exist_ok=True)
                dest_file = os.path.join(backup_path, filename)
                shutil.copy2(temp_file, dest_file)
                
                dest_size = os.path.getsize(dest_file)
                if dest_size != file_size:
                    raise Exception(f"复制后文件大小不一致: {dest_size} != {file_size}")
                
                results.append({
                    "path": backup_path,
                    "label": path_label,
                    "success": True,
                    "file": dest_file,
                    "size": dest_size,
                })
                logger.info(f"备份成功 [{path_label}]: {dest_file} ({dest_size} bytes)")
                
                clean_old_backups(backup_path, config.get("keep_days", 30))
                
            except PermissionError:
                failed_paths.append(backup_path)
                results.append({
                    "path": backup_path,
                    "label": path_label,
                    "success": False,
                    "error": "权限不足，无法写入",
                })
                logger.error(f"备份失败 [{path_label}]: 权限不足 - {backup_path}")
            except Exception as e:
                failed_paths.append(backup_path)
                results.append({
                    "path": backup_path,
                    "label": path_label,
                    "success": False,
                    "error": str(e),
                })
                logger.error(f"备份失败 [{path_label}]: {e}")
        
        # Git 备份（独立于三个文件位置）
        git_config = config.get("git_config", DEFAULT_GIT_CONFIG)
        git_result = git_backup(temp_file, filename, git_config)
        repo_path = get_project_root()
        results.append({
            "path": repo_path,
            "label": "Git仓库",
            "success": git_result["success"],
            "error": git_result.get("message", ""),
            "skipped": git_result.get("skipped", False),
            "type": "git",
        })
        if not git_result["success"] and not git_result.get("skipped"):
            failed_paths.append(f"Git: {git_result.get('message', '')}")
        
        success = len(failed_paths) == 0
        update_status(status, success, results, failed_paths)
        
        return {
            "success": success,
            "results": results,
            "failed_paths": failed_paths,
            "filename": filename,
            "size": file_size,
        }
        
    except subprocess.TimeoutExpired:
        logger.error("pg_dump 执行超时")
        update_status(status, False, [], backup_paths)
        return {"success": False, "error": "备份超时(10分钟)", "results": [], "failed_paths": backup_paths}
    except Exception as e:
        logger.error(f"备份异常: {e}")
        update_status(status, False, [], backup_paths)
        return {"success": False, "error": str(e), "results": [], "failed_paths": backup_paths}
    finally:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass


def update_status(status, success, results=None, failed_paths=None):
    """更新备份状态"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status["last_backup_time"] = now
    status["last_backup_success"] = success
    if results is not None:
        status["backup_results"] = results
    if failed_paths is not None:
        status["failed_paths"] = failed_paths
        if failed_paths:
            status["consecutive_failures"] = status.get("consecutive_failures", 0) + 1
        else:
            status["consecutive_failures"] = 0
    save_status(status)


def clean_old_backups(backup_path, keep_days):
    """清理超过保留天数的备份文件"""
    try:
        cutoff = datetime.now().timestamp() - (keep_days * 86400)
        for f in os.listdir(backup_path):
            if f.startswith("taiping_education_") and f.endswith(".sql"):
                fpath = os.path.join(backup_path, f)
                if os.path.getmtime(fpath) < cutoff:
                    os.remove(fpath)
                    logger.info(f"已清理过期备份: {f}")
    except Exception as e:
        logger.warning(f"清理过期备份时出错: {e}")


def daily_backup_job():
    """定时备份任务（由调度器调用）"""
    logger.info("=" * 50)
    logger.info("开始执行每日自动备份...")
    result = run_backup()
    if result["success"]:
        logger.info(f"每日备份成功: {result.get('filename', '')}")
    else:
        logger.error(f"每日备份失败: {result.get('error', '') or result.get('failed_paths', [])}")
    logger.info("=" * 50)
    return result