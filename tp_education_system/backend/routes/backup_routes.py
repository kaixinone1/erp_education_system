"""
系统自动备份与更新管理 API
功能：一键备份到本地+远程Git、检查更新、安装更新、回滚、错误报告
"""
import subprocess
import os
import json
import datetime
import shutil
import glob as glob_m
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/system/backup", tags=["系统备份与更新"])

# 项目根目录（自动检测Git仓库根目录）
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
    # 回退
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

PROJECT_ROOT = _get_project_root()
BACKUP_DIR = os.path.join(PROJECT_ROOT, "备份")
DB_NAME = "taiping_education"
DB_USER = "taiping_user"
DB_PASSWORD = "taiping_password"
DB_HOST = "localhost"
DB_PORT = "5432"


def _run_git(cmd: list, cwd: str = PROJECT_ROOT) -> dict:
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


def _find_pg_dump() -> Optional[str]:
    """查找 pg_dump 路径"""
    candidates = glob_m.glob(r"C:\Program Files\PostgreSQL\*\bin\pg_dump.exe")
    if candidates:
        return candidates[0]
    return None


def _get_db_connection():
    """获取数据库连接"""
    import psycopg2
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )


# ==================== API 端点 ====================

@router.get("/status")
def get_backup_status():
    """获取系统备份与 Git 状态"""
    status_info = {
        "git_available": False,
        "remote_configured": False,
        "remote_url": "",
        "current_branch": "",
        "latest_commit": "",
        "latest_commit_time": "",
        "latest_commit_message": "",
        "uncommitted_changes": False,
        "unpushed_commits": 0,
        "last_backup_time": "",
        "last_backup_file": "",
        "remote_updates_available": False,
        "remote_commits_behind": 0,
    }

    # Git 状态
    git_result = _run_git(["--version"])
    if git_result["success"]:
        status_info["git_available"] = True

    # 远程仓库
    remote_result = _run_git(["remote", "get-url", "origin"])
    if remote_result["success"]:
        status_info["remote_configured"] = True
        status_info["remote_url"] = remote_result["stdout"]

    # 当前分支
    branch_result = _run_git(["branch", "--show-current"])
    if branch_result["success"]:
        status_info["current_branch"] = branch_result["stdout"]

    # 最新提交
    log_result = _run_git(["log", "-1", "--format=%H|%ai|%s"])
    if log_result["success"] and log_result["stdout"]:
        parts = log_result["stdout"].split("|", 2)
        if len(parts) >= 3:
            status_info["latest_commit"] = parts[0][:8]
            status_info["latest_commit_time"] = parts[1]
            status_info["latest_commit_message"] = parts[2]

    # 未提交变更
    status_result = _run_git(["status", "--porcelain"])
    if status_result["success"]:
        status_info["uncommitted_changes"] = len(status_result["stdout"].strip()) > 0

    # 未推送提交
    if status_info["remote_configured"]:
        fetch_result = _run_git(["fetch", "origin"])
        behind_result = _run_git(["rev-list", "--count", "HEAD..origin/main"])
        if behind_result["success"] and behind_result["stdout"].strip().isdigit():
            status_info["remote_updates_available"] = int(behind_result["stdout"].strip()) > 0
            status_info["remote_commits_behind"] = int(behind_result["stdout"].strip())

        ahead_result = _run_git(["rev-list", "--count", "origin/main..HEAD"])
        if ahead_result["success"] and ahead_result["stdout"].strip().isdigit():
            status_info["unpushed_commits"] = int(ahead_result["stdout"].strip())

    # 最后备份时间
    if os.path.exists(BACKUP_DIR):
        sql_files = glob_m.glob(os.path.join(BACKUP_DIR, "taiping_education_*.sql"))
        if sql_files:
            latest = max(sql_files, key=os.path.getmtime)
            status_info["last_backup_time"] = datetime.datetime.fromtimestamp(
                os.path.getmtime(latest)
            ).strftime("%Y-%m-%d %H:%M:%S")
            status_info["last_backup_file"] = os.path.basename(latest)

    return {"success": True, "data": status_info}


@router.post("/create")
def create_backup():
    """创建完整系统备份：数据库 + 代码提交 + 推送到远程"""
    results = {
        "database_backup": None,
        "git_commit": None,
        "git_push": None,
        "backup_file": "",
        "errors": []
    }

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. 数据库备份
    pg_dump_path = _find_pg_dump()
    if pg_dump_path:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        sql_file = os.path.join(BACKUP_DIR, f"taiping_education_{timestamp}.sql")

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
                results["database_backup"] = f"成功 ({size_mb:.2f} MB)"
                results["backup_file"] = sql_file
            else:
                results["database_backup"] = f"失败: {result.stderr}"
                results["errors"].append(f"数据库备份失败: {result.stderr}")
        except Exception as e:
            results["database_backup"] = f"失败: {str(e)}"
            results["errors"].append(f"数据库备份异常: {str(e)}")
    else:
        results["database_backup"] = "跳过（未找到 pg_dump）"
        results["errors"].append("未找到 PostgreSQL pg_dump 工具")

    # 2. Git 提交
    git_status = _run_git(["status", "--porcelain"])
    if git_status["success"] and git_status["stdout"].strip():
        # 有变更，执行提交
        add_result = _run_git(["add", "-A"])
        if add_result["success"]:
            commit_msg = f"自动备份：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            commit_result = _run_git(["commit", "-m", commit_msg])
            if commit_result["success"]:
                results["git_commit"] = "成功"
            else:
                results["git_commit"] = f"失败: {commit_result['stderr']}"
                results["errors"].append(f"Git 提交失败: {commit_result['stderr']}")
        else:
            results["git_commit"] = f"失败: {add_result['stderr']}"
    elif git_status["success"]:
        results["git_commit"] = "无变更，跳过提交"
    else:
        results["git_commit"] = f"失败: {git_status['stderr']}"

    # 3. Git 推送到远程
    push_result = _run_git(["push", "origin", "main"])
    if push_result["success"]:
        results["git_push"] = "成功"
    else:
        results["git_push"] = f"失败: {push_result['stderr']}"
        results["errors"].append(f"Git 推送失败: {push_result['stderr']}")

    # 整体成功判断
    overall_success = len(results["errors"]) == 0
    return {
        "success": overall_success,
        "message": "备份完成" if overall_success else f"备份部分失败，共 {len(results['errors'])} 个错误",
        "details": results
    }


@router.post("/push")
def push_to_remote():
    """推送本地提交到远程 Git 仓库"""
    push_result = _run_git(["push", "origin", "main"])
    if push_result["success"]:
        return {"success": True, "message": "推送成功", "stdout": push_result["stdout"]}
    else:
        raise HTTPException(status_code=500, detail=f"推送失败: {push_result['stderr']}")


@router.get("/check-updates")
def check_updates():
    """检查远程仓库是否有更新"""
    fetch_result = _run_git(["fetch", "origin"])
    if not fetch_result["success"]:
        raise HTTPException(status_code=500, detail=f"无法连接远程仓库: {fetch_result['stderr']}")

    behind_result = _run_git(["rev-list", "--count", "HEAD..origin/main"])
    behind_count = 0
    if behind_result["success"] and behind_result["stdout"].strip().isdigit():
        behind_count = int(behind_result["stdout"].strip())

    # 获取远程更新日志
    updates = []
    if behind_count > 0:
        log_result = _run_git(["log", f"-{behind_count}", "--oneline", "HEAD..origin/main"])
        if log_result["success"]:
            updates = log_result["stdout"].split("\n") if log_result["stdout"] else []

    return {
        "success": True,
        "updates_available": behind_count > 0,
        "commits_behind": behind_count,
        "update_log": updates
    }


@router.post("/pull-updates")
def pull_updates():
    """从远程拉取更新"""
    updates = {
        "pulled": False,
        "commits": [],
        "errors": [],
        "before_commit": "",
        "after_commit": ""
    }

    # 记录当前提交
    before = _run_git(["rev-parse", "HEAD"])
    updates["before_commit"] = before["stdout"][:8] if before["success"] else "未知"

    # 拉取更新
    pull_result = _run_git(["pull", "origin", "main"])
    if not pull_result["success"]:
        updates["errors"].append(f"拉取失败: {pull_result['stderr']}")
        raise HTTPException(status_code=500, detail=f"拉取更新失败: {pull_result['stderr']}")

    updates["pulled"] = True

    # 记录更新后提交
    after = _run_git(["rev-parse", "HEAD"])
    updates["after_commit"] = after["stdout"][:8] if after["success"] else "未知"

    # 获取更新日志
    if updates["before_commit"] != updates["after_commit"]:
        log_result = _run_git(["log", "--oneline", f"{updates['before_commit']}..{updates['after_commit']}"])
        if log_result["success"] and log_result["stdout"]:
            updates["commits"] = log_result["stdout"].split("\n")

    return {
        "success": True,
        "message": f"成功拉取更新（{len(updates['commits'])} 个提交）",
        "details": updates
    }


@router.post("/rollback")
def rollback():
    """回滚到上一个提交"""
    rollback_info = {
        "before_commit": "",
        "after_commit": "",
        "rolled_back_commits": []
    }

    before = _run_git(["rev-parse", "HEAD"])
    rollback_info["before_commit"] = before["stdout"][:8] if before["success"] else "未知"

    # 获取要回滚的提交
    log_result = _run_git(["log", "-1", "--oneline"])
    if log_result["success"]:
        rollback_info["rolled_back_commits"].append(log_result["stdout"])

    # 执行回滚
    reset_result = _run_git(["reset", "--hard", "HEAD~1"])
    if not reset_result["success"]:
        raise HTTPException(status_code=500, detail=f"回滚失败: {reset_result['stderr']}")

    after = _run_git(["rev-parse", "HEAD"])
    rollback_info["after_commit"] = after["stdout"][:8] if after["success"] else "未知"

    return {
        "success": True,
        "message": f"已回滚到 {rollback_info['after_commit']}",
        "details": rollback_info
    }


@router.get("/history")
def get_backup_history(limit: int = 20):
    """获取备份/提交历史"""
    log_result = _run_git(["log", f"-{limit}", "--format=%H|%ai|%s"])
    if not log_result["success"]:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {log_result['stderr']}")

    history = []
    for line in log_result["stdout"].split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 2)
        if len(parts) >= 3:
            history.append({
                "commit_hash": parts[0][:8],
                "commit_time": parts[1],
                "commit_message": parts[2]
            })

    # 同时列出本地备份文件
    backup_files = []
    if os.path.exists(BACKUP_DIR):
        sql_files = sorted(
            glob_m.glob(os.path.join(BACKUP_DIR, "taiping_education_*.sql")),
            key=os.path.getmtime,
            reverse=True
        )
        for f in sql_files[:limit]:
            backup_files.append({
                "file_name": os.path.basename(f),
                "file_size_mb": round(os.path.getsize(f) / (1024 * 1024), 2),
                "backup_time": datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")
            })

    return {
        "success": True,
        "git_history": history,
        "backup_files": backup_files
    }


@router.post("/restore-db")
def restore_database(data: dict):
    """从备份文件恢复数据库"""
    backup_file = data.get("backup_file", "")
    if not backup_file:
        raise HTTPException(status_code=400, detail="请指定备份文件")

    full_path = os.path.join(BACKUP_DIR, backup_file) if not os.path.isabs(backup_file) else backup_file
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"备份文件不存在: {backup_file}")

    # 使用 psql 恢复
    psql_paths = glob_m.glob(r"C:\Program Files\PostgreSQL\*\bin\psql.exe")
    if not psql_paths:
        raise HTTPException(status_code=500, detail="未找到 psql 工具")

    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    cmd = [
        psql_paths[0],
        "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, "-d", DB_NAME,
        "-f", full_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600)
        if result.returncode == 0:
            return {"success": True, "message": "数据库恢复成功"}
        else:
            raise HTTPException(status_code=500, detail=f"数据库恢复失败: {result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="数据库恢复超时")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库恢复异常: {str(e)}")


@router.post("/generate-error-report")
def generate_error_report(data: dict):
    """生成错误报告（更新失败时调用）"""
    error_description = data.get("误差描述", "")
    update_version = data.get("更新版本", "")
    error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_dir = os.path.join(PROJECT_ROOT, "错误报告")
    os.makedirs(report_dir, exist_ok=True)

    report_file = os.path.join(report_dir, f"错误报告_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    report_content = f"""========================================
  系统更新错误报告
  生成时间：{error_time}
========================================

【更新版本】{update_version}

【错误描述】
{error_description}

【系统状态】
- 当前 Git 提交：{_run_git(['rev-parse', 'HEAD'])['stdout'][:8] if _run_git(['rev-parse', 'HEAD'])['success'] else '未知'}
- 当前分支：{_run_git(['branch', '--show-current'])['stdout']}

【最近提交历史】
{_run_git(['log', '-5', '--oneline'])['stdout']}

【数据库状态】
- 数据库名：{DB_NAME}
- 主机：{DB_HOST}:{DB_PORT}

========================================
  请将此报告发送给开发团队以获取支持
========================================
"""

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    return {
        "success": True,
        "message": "错误报告已生成",
        "report_file": report_file,
        "report_content": report_content
    }


@router.get("/git-log")
def get_git_log(limit: int = 30):
    """获取 Git 日志（详细版）"""
    log_result = _run_git(["log", f"-{limit}", "--format=%H|%ai|%an|%s"])
    if not log_result["success"]:
        raise HTTPException(status_code=500, detail=log_result["stderr"])

    commits = []
    for line in log_result["stdout"].split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 3)
        if len(parts) >= 4:
            commits.append({
                "hash": parts[0][:8],
                "time": parts[1],
                "author": parts[2],
                "message": parts[3]
            })

    return {"success": True, "commits": commits}