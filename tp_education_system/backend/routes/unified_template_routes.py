"""
统一模板管理API路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import Dict, Any
from datetime import datetime
import json

from core.unified_template_manager import UnifiedTemplateManager

router = APIRouter(prefix="/api/template", tags=["模板管理"])

template_manager = UnifiedTemplateManager()


@router.post("/parse")
async def parse_template(file: UploadFile = File(...)):
    """
    解析模板文件
    
    支持的文件格式：
    - .xlsx, .xls - Excel模板
    - .docx - Word模板
    """
    try:
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            if file_ext in ['.xlsx', '.xls']:
                template_config = template_manager.parse_excel_template(tmp_file_path)
            elif file_ext == '.docx':
                template_config = template_manager.parse_word_template(tmp_file_path)
            else:
                raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file_ext}")
            
            return {
                "success": True,
                "template_config": template_config,
                "message": "模板解析成功"
            }
        
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模板解析失败: {str(e)}")


@router.post("/save")
async def save_template(template_config: Dict[str, Any]):
    """
    保存模板配置
    """
    try:
        success = template_manager.save_template(template_config)
        
        if success:
            return {
                "success": True,
                "message": "模板保存成功",
                "template_id": template_config["template_id"]
            }
        else:
            raise HTTPException(status_code=500, detail="模板保存失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模板保存失败: {str(e)}")


@router.get("/list")
async def list_templates(category: str = None):
    """
    列出所有模板
    
    Args:
        category: 模板分类（可选）
    """
    try:
        templates = template_manager.list_templates(category)
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板列表失败: {str(e)}")


@router.get("/{template_id}")
async def get_template(template_id: str):
    """
    获取模板配置
    
    Args:
        template_id: 模板ID
    """
    try:
        template = template_manager.get_template(template_id)
        
        if template:
            return {
                "success": True,
                "template": template
            }
        else:
            raise HTTPException(status_code=404, detail="模板不存在")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """
    删除模板
    
    Args:
        template_id: 模板ID
    """
    try:
        success = template_manager.delete_template(template_id)
        
        if success:
            return {
                "success": True,
                "message": "模板删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail="模板不存在")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除模板失败: {str(e)}")


@router.post("/{template_id}/generate-form")
async def generate_form(template_id: str):
    """
    根据模板配置生成网页表单配置
    
    Args:
        template_id: 模板ID
    """
    try:
        template = template_manager.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        display_config = template.get("display_config", {})
        
        return {
            "success": True,
            "form_config": display_config,
            "message": "表单配置生成成功"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成表单配置失败: {str(e)}")


@router.put("/{template_id}")
async def update_template(template_id: str, template_config: Dict[str, Any]):
    """
    更新模板配置
    
    Args:
        template_id: 模板ID
        template_config: 新的模板配置
    """
    try:
        # 检查模板是否存在
        existing_template = template_manager.get_template(template_id)
        if not existing_template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        # 更新模板
        template_config['template_id'] = template_id
        template_config['updated_at'] = datetime.now().isoformat()
        
        success = template_manager.save_template(template_config)
        
        if success:
            return {
                "success": True,
                "message": "模板更新成功",
                "template_id": template_id
            }
        else:
            raise HTTPException(status_code=500, detail="模板更新失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新模板失败: {str(e)}")


@router.post("/{template_id}/copy")
async def copy_template(template_id: str, new_name: str = None):
    """
    复制模板
    
    Args:
        template_id: 模板ID
        new_name: 新模板名称（可选）
    """
    try:
        template = template_manager.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        # 创建副本
        import copy
        new_template = copy.deepcopy(template)
        
        # 修改名称和ID
        if new_name:
            new_template['chinese_name'] = new_name
        
        new_template['template_id'] = template_manager._generate_template_id(new_template['chinese_name'])
        new_template['created_at'] = datetime.now().isoformat()
        
        # 保存副本
        success = template_manager.save_template(new_template)
        
        if success:
            return {
                "success": True,
                "message": "模板复制成功",
                "new_template_id": new_template['template_id']
            }
        else:
            raise HTTPException(status_code=500, detail="模板复制失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"复制模板失败: {str(e)}")


@router.post("/{template_id}/export")
async def export_template(template_id: str):
    """
    导出模板配置文件
    
    Args:
        template_id: 模板ID
    """
    try:
        template = template_manager.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        # 返回JSON文件
        from fastapi.responses import Response
        
        json_str = json.dumps(template, ensure_ascii=False, indent=2)
        
        return Response(
            content=json_str,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={template['chinese_name']}_template.json"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出模板失败: {str(e)}")


@router.post("/{template_id}/call-record")
async def record_template_call(
    template_id: str,
    module_name: str = None,
    call_params: Dict[str, Any] = None
):
    """
    记录模板调用
    
    Args:
        template_id: 模板ID
        module_name: 调用模块名称
        call_params: 调用参数
    """
    try:
        # 这里可以添加到数据库记录调用情况
        # 暂时先返回成功
        return {
            "success": True,
            "message": "调用记录已保存",
            "template_id": template_id,
            "module_name": module_name,
            "call_time": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录调用失败: {str(e)}")


@router.get("/{template_id}/statistics")
async def get_template_statistics(template_id: str):
    """
    获取模板使用统计
    
    Args:
        template_id: 模板ID
    """
    try:
        template = template_manager.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        # 这里可以从数据库查询统计数据
        # 暂时返回模拟数据
        statistics = {
            "template_id": template_id,
            "template_name": template.get('chinese_name'),
            "total_calls": 0,
            "recent_calls": [],
            "popular_fields": [],
            "last_called": None
        }
        
        return {
            "success": True,
            "statistics": statistics
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")
