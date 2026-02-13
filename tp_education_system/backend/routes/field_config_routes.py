from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
from core.field_config_manager import field_config_manager

router = APIRouter(prefix="/api/field-configs", tags=["field-configs"])

# 配置文件保存目录（向后兼容）
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'field_configs')


def ensure_config_dir():
    """确保配置目录存在"""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def get_config_file_path(config_name: str) -> str:
    """获取配置文件路径"""
    ensure_config_dir()
    # 清理文件名，移除不合法字符
    safe_name = "".join(c for c in config_name if c.isalnum() or c in ('_', '-', ' ', '.'))
    safe_name = safe_name.strip()
    if not safe_name.endswith('.json'):
        safe_name += '.json'
    return os.path.join(CONFIG_DIR, safe_name)


def read_config_file(file_path: str) -> Optional[Dict[str, Any]]:
    """读取配置文件"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"读取配置文件失败 {file_path}: {e}")
        return None


@router.get("/list")
async def list_configs():
    """获取所有字段配置文件列表"""
    try:
        # 使用 FieldConfigManager 获取所有配置
        configs = field_config_manager.get_all_configs()

        # 只返回字段配置文件（配置名称以"字段配置"结尾）
        result = []
        for config in configs:
            config_name = config.get('config_name', '')
            # 只显示以"字段配置"结尾的配置文件
            if config_name.endswith('字段配置'):
                result.append({
                    "name": config_name,
                    "display_name": config_name,
                    "table_name": config.get('table_name', ''),
                    "chinese_title": config_name,
                    "created_at": config.get('created_at', ''),
                    "updated_at": config.get('updated_at', ''),
                    "field_count": len(config.get('field_mappings', [])),
                    "version": config.get('version', 1),
                    "is_latest": config.get('is_latest', True)
                })

        # 按更新时间排序
        result.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        return {"configs": result}
    except Exception as e:
        print(f"获取配置文件列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置文件列表失败: {str(e)}")


@router.get("/{config_name}")
async def get_config(config_name: str):
    """获取指定配置文件内容"""
    try:
        # 优先从 FieldConfigManager 获取
        config = field_config_manager.get_config_by_name(config_name)
        
        if config:
            # 转换为前端需要的格式
            return {
                'config_id': config.get('id', ''),
                'config_name': config.get('config_name', ''),
                'display_name': config.get('config_name', ''),
                'chinese_title': config.get('config_name', ''),
                'table_name': config.get('table_name', ''),
                'table_type': config.get('table_type', 'master'),
                'parent_table': config.get('parent_table', ''),
                'field_configs': config.get('field_mappings', []),
                'created_at': config.get('created_at', ''),
                'updated_at': config.get('updated_at', '')
            }
        
        # 如果找不到，尝试从单个文件读取（向后兼容）
        file_path = get_config_file_path(config_name)
        config = read_config_file(file_path)
        
        if config:
            return config
        else:
            raise HTTPException(status_code=404, detail="配置文件不存在")
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置文件失败: {str(e)}")


@router.post("/save")
async def save_config(data: Dict[str, Any]):
    """保存配置文件"""
    try:
        config_name = data.get("config_name", "")
        table_name = data.get("table_name", "")
        
        if not config_name:
            raise HTTPException(status_code=400, detail="配置文件名称不能为空")
        
        # 准备配置数据
        config_data = {
            'config_name': config_name,
            'table_name': table_name,
            'table_type': data.get("table_type", "master"),
            'parent_table': data.get("parent_table", ""),
            'source_file_pattern': data.get("source_file_pattern", f"*{config_name}*"),
            'field_mappings': data.get("field_configs", []),
            'id': data.get("id")  # 如果有ID则更新，否则新建
        }
        
        # 使用 FieldConfigManager 保存
        result = field_config_manager.save_config(config_data)
        
        if not result.get('success'):
            status = result.get('status', 'error')
            return {
                "status": status,
                "message": result.get('message', '保存失败'),
                "config_name": config_name
            }
        
        return {
            "status": "success",
            "message": result.get('message', '保存成功'),
            "config_name": config_name,
            "config_id": result.get('config_id'),
            "is_new": result.get('is_new', True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存配置文件失败: {str(e)}")


@router.post("/save-as")
async def save_as_config(data: Dict[str, Any]):
    """另存为配置文件"""
    try:
        config_name = data.get("config_name", "")
        
        if not config_name:
            raise HTTPException(status_code=400, detail="配置文件名称不能为空")
        
        # 准备配置数据（不传入ID，强制新建）
        config_data = {
            'config_name': config_name,
            'table_name': data.get("table_name", ""),
            'table_type': data.get("table_type", "master"),
            'parent_table': data.get("parent_table", ""),
            'source_file_pattern': data.get("source_file_pattern", f"*{config_name}*"),
            'field_mappings': data.get("field_configs", [])
        }
        
        # 使用 FieldConfigManager 保存
        result = field_config_manager.save_config(config_data)
        
        if not result.get('success'):
            status = result.get('status', 'error')
            return {
                "status": status,
                "message": result.get('message', '保存失败'),
                "config_name": config_name
            }
        
        return {
            "status": "success",
            "message": result.get('message', '保存成功'),
            "config_name": config_name,
            "config_id": result.get('config_id'),
            "is_new": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"另存为配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"另存为配置文件失败: {str(e)}")


@router.delete("/{config_name}")
async def delete_config(config_name: str):
    """删除配置文件"""
    try:
        # 先查找配置ID
        config = field_config_manager.get_config_by_name(config_name)
        
        if not config:
            raise HTTPException(status_code=404, detail="配置文件不存在")
        
        config_id = config.get('id')
        
        # 使用 FieldConfigManager 删除
        result = field_config_manager.delete_config(config_id)
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('message', '删除失败'))
        
        return {
            "status": "success",
            "message": result.get('message', '删除成功')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除配置文件失败: {str(e)}")


@router.post("/match")
async def match_configs(data: Dict[str, Any]):
    """根据文件名查找匹配的配置"""
    try:
        filename = data.get("filename", "")
        
        if not filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 使用 FieldConfigManager 查找匹配的配置
        matching_configs = field_config_manager.find_matching_configs(filename)
        
        return {
            "status": "success",
            "message": f"找到 {len(matching_configs)} 个匹配的配置",
            "data": matching_configs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"查找匹配配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"查找匹配配置失败: {str(e)}")


@router.get("/global-mappings/list")
async def get_global_mappings():
    """获取全局字段映射"""
    try:
        mappings = field_config_manager.get_global_mappings()
        
        return {
            "status": "success",
            "data": mappings
        }
        
    except Exception as e:
        print(f"获取全局字段映射失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取全局字段映射失败: {str(e)}")
