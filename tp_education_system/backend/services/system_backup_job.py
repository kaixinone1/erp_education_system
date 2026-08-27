"""
系统自动备份定时任务
- 数据库备份（pg_dump）
- Git 提交变更
- 推送到远程仓库
- 飞书通知备份结果
"""
import subprocess
import os
import glob as glob_m
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_NAME = "taiping_education"
DB_USER = "taiping_user"
DB_PASSWORD = "taiping_password"
DB_HOST = "localhost"
DB_PORT = "5432"


def _get_git_env():
    """获取Git操作的环境变量，禁止交互式提示"""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "echo"
    env["SSH_ASKPASS"] = "echo"
    env["GCM_INTERACTIVE"] = "Never"
    env["GCM_MODAL_PROMPT"] = "Never"
    env.setdefault("GIT_AUTHOR_NAME", "ERP系统自动备份")
    env.setdefault("GIT_AUTHOR_EMAIL", "backup@erp.local")
    env.setdefault("GIT_COMMITTER_NAME", "ERP系统自动备份")
    env.setdefault("GIT_COMMITTER_EMAIL", "backup@erp.local")
    # 加载GitHub Token
    github_token = _get_github_token()
    if github_token:
        env["GITHUB_TOKEN"] = github_token
        env["GH_TOKEN"] = github_token
    return env


def _get_github_token():
    """从数据库备份配置中读取GitHub Token"""
    try:
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        config_file = os.path.join(config_dir, 'db_backup_config.json')
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("git_config", {}).get("github_token", "")
    except Exception:
        pass
    return ""


def _get_project_root():
    """自动检测项目根目录（Git仓库根目录）"""
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _run_git(cmd: list, cwd: str) -> dict:
    """执行 Git 命令"""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace",
            env=_get_git_env()
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Git 命令执行超时", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def _find_pg_dump():
    """查找 pg_dump 路径"""
    candidates = glob_m.glob(r"C:\Program Files\PostgreSQL\*\bin\pg_dump.exe")
    if candidates:
        return candidates[0]
    return None


def _send_notification(success: bool, errors: list, backup_file: str = "", file_size: int = 0):
    """发送飞书通知"""
    try:
        from .feishu_notification_service import send_backup_notification
        result = {
            "success": success,
            "results": [],
            "failed_paths": errors if errors else [],
            "filename": backup_file or f"系统自动备份_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "size": file_size,
            "error": "; ".join(errors) if errors else "",
        }
        notify_result = send_backup_notification(result)
        if notify_result.get("skipped"):
            logger.info(f"飞书通知已跳过: {notify_result.get('reason')}")
        else:
            for r in notify_result.get("results", []):
                if r.get("success"):
                    logger.info(f"飞书通知已发送: {r.get('用户')}")
                else:
                    logger.warning(f"飞书通知发送失败: {r.get('用户')} - {r.get('error')}")
    except Exception as e:
        logger.warning(f"飞书通知发送异常: {e}")


def system_backup_job():
    """系统自动备份任务（由调度器调用）"""
    logger.info("=" * 50)
    logger.info("开始执行系统自动备份...")
    
    project_root = _get_project_root()
    backup_dir = os.path.join(project_root, "备份")
    errors = []
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = ""
    file_size = 0

    # 1. 数据库备份
    pg_dump_path = _find_pg_dump()
    if pg_dump_path:
        os.makedirs(backup_dir, exist_ok=True)
        sql_file = os.path.join(backup_dir, f"taiping_education_{timestamp}.sql")
        backup_file = sql_file
        
        cmd = [
            pg_dump_path,
            "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, "-d", DB_NAME,
            "-f", sql_file, "--encoding", "UTF8", "--no-owner", "--no-privileges"
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=300)
            if result.returncode == 0:
                file_size = os.path.getsize(sql_file)
                size_mb = file_size / (1024 * 1024)
                logger.info(f"数据库备份成功 ({size_mb:.2f} MB): {sql_file}")
            else:
                errors.append(f"数据库备份失败: {result.stderr}")
                logger.error(f"数据库备份失败: {result.stderr}")
        except Exception as e:
            errors.append(f"数据库备份异常: {str(e)}")
            logger.error(f"数据库备份异常: {e}")
    else:
        errors.append("未找到 PostgreSQL pg_dump 工具")
        logger.warning("未找到 pg_dump，跳过数据库备份")

    # 2. Git 提交
    git_status = _run_git(["status", "--porcelain"], project_root)
    if git_status["success"] and git_status["stdout"].strip():
        add_result = _run_git(["add", "-A"], project_root)
        if add_result["success"]:
            commit_msg = f"系统自动备份：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            commit_result = _run_git(["commit", "-m", commit_msg], project_root)
            if commit_result["success"]:
                logger.info(f"Git 提交成功: {commit_msg}")
            else:
                errors.append(f"Git 提交失败: {commit_result['stderr']}")
                logger.error(f"Git 提交失败: {commit_result['stderr']}")
        else:
            errors.append(f"Git add 失败: {add_result['stderr']}")
    elif git_status["success"]:
        logger.info("Git: 无变更，跳过提交")
    else:
        errors.append(f"Git status 失败: {git_status['stderr']}")

    # 3. Git 推送到远程
    github_token = _get_github_token()
    if github_token:
        # 使用token认证推送：将token嵌入remote URL
        push_result = _run_git([
            "push",
            f"https://{github_token}@github.com/kaixinone1/erp_education_system",
            "main"
        ], project_root)
    else:
        push_result = _run_git(["push", "origin", "main"], project_root)
    if push_result["success"]:
        logger.info("Git 推送成功")
    else:
        errors.append(f"Git 推送失败: {push_result['stderr']}")
        logger.error(f"Git 推送失败: {push_result['stderr']}")

    if errors:
        logger.error(f"系统自动备份完成，有 {len(errors)} 个错误: {errors}")
    else:
        logger.info("系统自动备份完成，全部成功")

    # 4. 发送飞书通知
    _send_notification(len(errors) == 0, errors, backup_file, file_size)
    
    logger.info("=" * 50)
    return {"success": len(errors) == 0, "errors": errors}