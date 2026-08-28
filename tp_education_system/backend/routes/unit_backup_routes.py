"""
按单位备份和恢复 API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.unit_backup_service import (
    get_units,
    backup_unit,
    backup_all_units,
    restore_unit,
    get_unit_backup_history,
    get_operation_logs,
)

router = APIRouter(prefix="/api/unit-backup", tags=["按单位备份"])


class RestoreRequest(BaseModel):
    unit_name: str
    backup_filename: str


@router.get("/units")
def list_units():
    """获取所有单位列表（含教师数量）"""
    try:
        units = get_units()
        return {"success": True, "data": units}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{unit_name}")
def backup_history(unit_name: str):
    """获取指定单位的备份历史"""
    try:
        history = get_unit_backup_history(unit_name)
        return {"success": True, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backup/{unit_name}")
def run_unit_backup(unit_name: str):
    """备份指定单位"""
    try:
        result = backup_unit(unit_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backup-all")
def run_backup_all():
    """备份所有单位"""
    try:
        result = backup_all_units()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore")
def run_restore(req: RestoreRequest):
    """恢复指定单位"""
    try:
        result = restore_unit(req.unit_name, req.backup_filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
def operation_logs(limit: int = 50):
    """获取操作日志"""
    try:
        logs = get_operation_logs(limit)
        return {"success": True, "data": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))