"""
统一模板管理API路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import Dict, Any

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
