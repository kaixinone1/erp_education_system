"""
系统自动备份定时任务
- 数据库备份（pg_dump）
- Git 提交变更
- 推送到远程仓库
"""
import subprocess
import os
import glob as glob_m
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_NAME = "taiping_education"
DB_USER = "taiping_user"
DB_PASSWORD = "taiping_password"
DB_HOST = "localhost"
DB_PORT = "5432"


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
            errors="replace"
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


def system_backup_job():
    """系统自动备份任务（由调度器调用）"""
    logger.info("=" * 50)
    logger.info("开始执行系统自动备份...")
    
    project_root = _get_project_root()
    backup_dir = os.path.join(project_root, "备份")
    errors = []
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. 数据库备份
    pg_dump_path = _find_pg_dump()
    if pg_dump_path:
        os.makedirs(backup_dir, exist_ok=True)
        sql_file = os.path.join(backup_dir, f"taiping_education_{timestamp}.sql")
        
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
                size_mb = os.path.getsize(sql_file) / (1024 * 1024)
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
    
    logger.info("=" * 50)
    return {"success": len(errors) == 0, "errors": errors}