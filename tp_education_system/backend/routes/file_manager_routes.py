"""
文件管理路由 - 列出、预览、删除系统生成的导出文件
"""
import os
import shutil
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/file-manager", tags=["文件管理"])

# 导出文件目录
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports', 'templates')
SAVED_DIR = os.path.join(EXPORTS_DIR, '已保存')


def _get_all_files():
    """获取所有导出文件（包括已保存目录）"""
    files = []
    # 扫描 exports/templates 根目录
    if os.path.exists(EXPORTS_DIR):
        for fname in os.listdir(EXPORTS_DIR):
            fpath = os.path.join(EXPORTS_DIR, fname)
            if os.path.isfile(fpath):
                stat = os.stat(fpath)
                files.append({
                    "文件名": fname,
                    "路径": f"templates/{fname}",
                    "大小": stat.st_size,
                    "大小显示": _format_size(stat.st_size),
                    "修改时间": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    "类型": os.path.splitext(fname)[1].lower(),
                })
    # 扫描 exports/templates/已保存 目录
    if os.path.exists(SAVED_DIR):
        for fname in os.listdir(SAVED_DIR):
            fpath = os.path.join(SAVED_DIR, fname)
            if os.path.isfile(fpath):
                stat = os.stat(fpath)
                files.append({
                    "文件名": fname,
                    "路径": f"templates/已保存/{fname}",
                    "大小": stat.st_size,
                    "大小显示": _format_size(stat.st_size),
                    "修改时间": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    "类型": os.path.splitext(fname)[1].lower(),
                })
    # 按修改时间倒序
    files.sort(key=lambda x: x["修改时间"], reverse=True)
    return files


def _format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _safe_path(relative_path):
    """安全检查：确保路径在导出目录内"""
    base = os.path.abspath(EXPORTS_DIR)
    target = os.path.abspath(os.path.join(os.path.dirname(EXPORTS_DIR), relative_path))
    if not target.startswith(base):
        raise HTTPException(status_code=403, detail="禁止访问该路径")
    return target


@router.get("/list")
async def list_files():
    """列出所有导出文件"""
    try:
        files = _get_all_files()
        return {"成功": True, "数据": files, "总数": len(files)}
    except Exception as e:
        return {"成功": False, "错误": str(e)}


@router.get("/preview/{relative_path:path}")
async def preview_file(relative_path: str):
    """预览文件（PDF 直接返回，其他格式触发下载）"""
    try:
        file_path = _safe_path(relative_path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        ext = os.path.splitext(file_path)[1].lower()
        media_type_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.html': 'text/html',
        }
        media_type = media_type_map.get(ext, 'application/octet-stream')
        return FileResponse(file_path, media_type=media_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DeleteRequest(BaseModel):
    路径: str


class BatchDeleteRequest(BaseModel):
    路径列表: list


@router.post("/delete")
async def delete_file(req: DeleteRequest):
    """删除单个文件"""
    try:
        file_path = _safe_path(req.路径)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        os.remove(file_path)
        return {"成功": True, "消息": "文件已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-delete")
async def batch_delete_files(req: BatchDeleteRequest):
    """批量删除文件"""
    deleted = []
    failed = []
    for path in req.路径列表:
        try:
            file_path = _safe_path(path)
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted.append(path)
            else:
                failed.append({"路径": path, "原因": "文件不存在"})
        except Exception as e:
            failed.append({"路径": path, "原因": str(e)})
    return {
        "成功": True,
        "已删除": len(deleted),
        "失败": len(failed),
        "失败详情": failed if failed else None,
        "消息": f"成功删除 {len(deleted)} 个文件" + (f"，{len(failed)} 个失败" if failed else "")
    }