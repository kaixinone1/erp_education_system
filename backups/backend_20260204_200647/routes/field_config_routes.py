from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

router = APIRouter(prefix="/api/field-configs", tags=["field-configs"])

# 配置文件保存目录
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


def write_config_file(file_path: str, data: Dict[str, Any]) -> bool:
    """写入配置文件"""
    try:
        ensure_config_dir()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"写入配置文件失败 {file_path}: {e}")
        return False


@router.get("/list")
async def list_configs():
    """获取所有配置文件列表"""
    try:
        ensure_config_dir()
        configs = []
        
        for filename in os.listdir(CONFIG_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(CONFIG_DIR, filename)
                config = read_config_file(file_path)
                if config:
                    configs.append({
                        "name": filename[:-5],  # 移除.json后缀
                        "display_name": config.get("display_name", filename[:-5]),
                        "table_name": config.get("table_name", ""),
                        "chinese_title": config.get("chinese_title", ""),
                        "created_at": config.get("created_at", ""),
                        "updated_at": config.get("updated_at", ""),
                        "field_count": len(config.get("field_configs", []))
                    })
        
        # 按更新时间排序
        configs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return {"configs": configs}
    except Exception as e:
        print(f"获取配置文件列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置文件列表失败: {str(e)}")


@router.get("/{config_name}")
async def get_config(config_name: str):
    """获取指定配置文件内容"""
    try:
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
        display_name = data.get("display_name", config_name)
        
        if not config_name:
            raise HTTPException(status_code=400, detail="配置文件名称不能为空")
        
        file_path = get_config_file_path(config_name)
        
        # 检查文件是否已存在
        file_exists = os.path.exists(file_path)
        overwrite = data.get("overwrite", False)
        
        if file_exists and not overwrite:
            # 文件已存在且不允许覆盖
            return {
                "status": "exists",
                "message": f"配置文件 '{config_name}' 已存在",
                "existing_file": config_name
            }
        
        # 构建配置数据
        config_data = {
            "config_name": config_name,
            "display_name": display_name,
            "table_name": data.get("table_name", ""),
            "chinese_title": data.get("chinese_title", ""),
            "table_type": data.get("table_type", "master"),
            "parent_table": data.get("parent_table", ""),
            "field_configs": data.get("field_configs", []),
            "created_at": data.get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat()
        }
        
        # 如果是新文件，设置创建时间
        if not file_exists:
            config_data["created_at"] = datetime.now().isoformat()
        else:
            # 保留原有的创建时间
            existing_config = read_config_file(file_path)
            if existing_config and "created_at" in existing_config:
                config_data["created_at"] = existing_config["created_at"]
        
        # 保存文件
        if write_config_file(file_path, config_data):
            return {
                "status": "success",
                "message": f"配置文件 '{config_name}' 保存成功",
                "config_name": config_name,
                "is_new": not file_exists
            }
        else:
            raise HTTPException(status_code=500, detail="保存配置文件失败")
    except HTTPException:
        raise
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存配置文件失败: {str(e)}")


@router.post("/save-as")
async def save_config_as(data: Dict[str, Any]):
    """另存为新的配置文件"""
    try:
        new_config_name = data.get("new_config_name", "")
        display_name = data.get("display_name", new_config_name)
        
        if not new_config_name:
            raise HTTPException(status_code=400, detail="新配置文件名称不能为空")
        
        file_path = get_config_file_path(new_config_name)
        
        # 检查文件是否已存在
        if os.path.exists(file_path):
            return {
                "status": "exists",
                "message": f"配置文件 '{new_config_name}' 已存在，请选择其他名称",
                "existing_file": new_config_name
            }
        
        # 构建配置数据
        config_data = {
            "config_name": new_config_name,
            "display_name": display_name,
            "table_name": data.get("table_name", ""),
            "chinese_title": data.get("chinese_title", ""),
            "table_type": data.get("table_type", "master"),
            "parent_table": data.get("parent_table", ""),
            "field_configs": data.get("field_configs", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 保存文件
        if write_config_file(file_path, config_data):
            return {
                "status": "success",
                "message": f"配置文件 '{new_config_name}' 创建成功",
                "config_name": new_config_name
            }
        else:
            raise HTTPException(status_code=500, detail="保存配置文件失败")
    except HTTPException:
        raise
    except Exception as e:
        print(f"另存配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"另存配置文件失败: {str(e)}")


@router.delete("/{config_name}")
async def delete_config(config_name: str):
    """删除配置文件"""
    try:
        file_path = get_config_file_path(config_name)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="配置文件不存在")
        
        os.remove(file_path)
        
        return {
            "status": "success",
            "message": f"配置文件 '{config_name}' 删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除配置文件失败: {str(e)}")


@router.get("/check/{config_name}")
async def check_config_exists(config_name: str):
    """检查配置文件是否存在"""
    try:
        file_path = get_config_file_path(config_name)
        exists = os.path.exists(file_path)
        
        return {
            "exists": exists,
            "config_name": config_name
        }
    except Exception as e:
        print(f"检查配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"检查配置文件失败: {str(e)}")
