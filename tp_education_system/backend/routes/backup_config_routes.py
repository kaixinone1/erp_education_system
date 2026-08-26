"""
数据库自动备份配置API
- 配置三个备份路径
- 查看备份状态
- 手动触发备份
- 前端弹窗提示备份失败
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/backup-config", tags=["数据库自动备份"])

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
BACKUP_CONFIG_FILE = os.path.join(CONFIG_DIR, 'db_backup_config.json')
STATUS_FILE = os.path.join(CONFIG_DIR, 'db_backup_status.json')


class BackupConfigModel(BaseModel):
    backup_paths: List[str]
    backup_time: Optional[str] = "01:00"
    keep_days: Optional[int] = 30
    enabled: Optional[bool] = True
    git_config: Optional[dict] = None


class BackupPathUpdate(BaseModel):
    index: int  # 0, 1, 2
    path: str


def _get_config():
    if os.path.exists(BACKUP_CONFIG_FILE):
        with open(BACKUP_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    from services.db_backup_service import DEFAULT_BACKUP_PATHS
    return {
        "backup_paths": DEFAULT_BACKUP_PATHS,
        "backup_time": "01:00",
        "keep_days": 30,
        "enabled": True,
    }


def _save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(BACKUP_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def _get_status():
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


@router.get("/config")
def get_backup_config():
    """获取备份配置"""
    from services.db_backup_service import DEFAULT_GIT_CONFIG
    config = _get_config()
    return {
        "success": True,
        "data": {
            "backup_paths": config.get("backup_paths", []),
            "backup_time": config.get("backup_time", "01:00"),
            "keep_days": config.get("keep_days", 30),
            "enabled": config.get("enabled", True),
            "git_config": config.get("git_config", DEFAULT_GIT_CONFIG),
        }
    }


@router.put("/config")
def update_backup_config(config: BackupConfigModel):
    """更新备份配置"""
    cfg = config.model_dump()
    _save_config(cfg)
    return {"success": True, "message": "备份配置已保存"}


@router.put("/path")
def update_backup_path(data: BackupPathUpdate):
    """更新单个备份路径"""
    if data.index < 0 or data.index > 2:
        raise HTTPException(status_code=400, detail="备份路径索引必须在0-2之间")
    
    config = _get_config()
    paths = config.get("backup_paths", ["", "", ""])
    paths[data.index] = data.path
    config["backup_paths"] = paths
    _save_config(config)
    
    return {"success": True, "message": f"备份位置{data.index + 1}已更新"}


@router.get("/status")
def get_backup_status():
    """获取备份状态（前端轮询此接口）"""
    status = _get_status()
    config = _get_config()
    
    # 检查是否有未解决的失败
    has_failure = False
    failed_details = []
    if status.get("failed_paths"):
        has_failure = True
        paths = config.get("backup_paths", [])
        for fp in status["failed_paths"]:
            idx = -1
            for i, p in enumerate(paths):
                if p == fp:
                    idx = i
                    break
            failed_details.append({
                "path": fp,
                "label": f"备份位置{idx + 1}" if idx >= 0 else "未知位置",
                "index": idx,
            })
    
    return {
        "success": True,
        "data": {
            "last_backup_time": status.get("last_backup_time"),
            "last_backup_success": status.get("last_backup_success"),
            "consecutive_failures": status.get("consecutive_failures", 0),
            "has_failure": has_failure,
            "failed_details": failed_details,
            "backup_results": status.get("backup_results", []),
        }
    }


@router.post("/run")
def run_backup_now():
    """手动触发备份"""
    from services.db_backup_service import run_backup
    result = run_backup()
    return {
        "success": result["success"],
        "data": result,
    }


@router.post("/acknowledge-failure")
def acknowledge_failure():
    """确认已查看备份失败（清除失败标记）"""
    from services.db_backup_service import save_status
    status = _get_status()
    status["failed_paths"] = []
    status["consecutive_failures"] = 0
    save_status(status)
    return {"success": True, "message": "已确认备份失败提示"}


@router.get("/available-drives")
def get_available_drives():
    """获取系统可用驱动器列表（供前端选择备份路径）"""
    import string
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append({"path": drive, "label": f"{letter}盘"})
    return {"success": True, "data": drives}


@router.post("/git/verify")
def verify_git_repo_api():
    """验证当前项目是否为有效的 Git 仓库（自动检测，无需传入路径）"""
    from services.db_backup_service import verify_git_repo
    return verify_git_repo()


@router.get("/git/status")
def get_git_status():
    """获取当前项目Git仓库状态（自动检测远程URL、分支等）"""
    from services.db_backup_service import get_project_root, get_git_remote_url, get_git_branch, find_git
    repo_path = get_project_root()
    git_exe = find_git()
    git_available = git_exe is not None
    is_git_repo = os.path.isdir(os.path.join(repo_path, ".git")) if repo_path else False
    
    remote_url = get_git_remote_url() if is_git_repo and git_available else None
    branch = get_git_branch() if is_git_repo and git_available else "main"
    
    return {
        "success": True,
        "data": {
            "repo_path": repo_path,
            "git_available": git_available,
            "is_git_repo": is_git_repo,
            "remote_url": remote_url,
            "branch": branch,
            "remote_configured": remote_url is not None,
        }
    }


@router.put("/git/config")
def update_git_config(data: dict):
    """更新 Git 备份配置（仓库路径自动检测，无需手动配置）"""
    config = _get_config()
    config["git_config"] = {
        "enabled": data.get("enabled", False),
        "remote_name": data.get("remote_name", "origin"),
        "branch": data.get("branch", "main"),
        "backup_subdir": data.get("backup_subdir", "数据库备份"),
    }
    _save_config(config)
    return {"success": True, "message": "Git备份配置已保存"}