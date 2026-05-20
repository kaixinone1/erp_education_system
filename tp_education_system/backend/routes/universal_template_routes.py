"""
通用模板自动填报系统API路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
import shutil
import tempfile
from datetime import datetime

from services.universal_template_service import template_engine, get_db_connection

router = APIRouter(prefix="/api/universal-template", tags=["通用模板自动填报"])

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'templates')
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports', 'templates')

os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)


class ImportTemplateRequest(BaseModel):
    模板名称: str
    模板类型: str


class FieldMappingRequest(BaseModel):
    模板ID: str
    字段名称: str
    行号: int
    列号: int
    数据源: str
    转换函数: Optional[str] = None
    默认值: Optional[str] = None


class FillTemplateRequest(BaseModel):
    模板ID: str
    查询条件: Dict[str, Any]


@router.get("/check-filename/{filename}")
async def check_filename(filename: str):
    """
    检测文件名是否已被其他模板使用
    
    返回:
        存在: bool, 引用模板列表: list
    """
    try:
        file_path = os.path.join(TEMPLATE_DIR, filename)
        disk_exists = os.path.exists(file_path)

        referenced_templates = []
        if disk_exists:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 模板ID, 模板名称 FROM template_configs WHERE 原始文件路径 = %s",
                (filename,)
            )
            for row in cursor.fetchall():
                referenced_templates.append({"模板ID": row[0], "模板名称": row[1]})
            cursor.close()
            conn.close()

        return {
            "成功": True,
            "磁盘存在": disk_exists,
            "被引用模板": referenced_templates,
            "有冲突": len(referenced_templates) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_template(
    file: UploadFile = File(...),
    模板名称: str = Form(...),
    模板类型: str = Form(...),
    保存文件名: str = Form(None)
):
    try:
        save_filename = 保存文件名 if 保存文件名 else file.filename
        temp_path = os.path.join(TEMPLATE_DIR, save_filename)
        with open(temp_path, 'wb') as f:
            f.write(file.file.read())
        
        config = template_engine.import_template(temp_path, 模板名称, 模板类型)
        
        template_engine.save_template_config(config)
        
        return {
            "成功": True,
            "消息": "模板导入成功",
            "数据": config
        }
    except Exception as e:
        import traceback
        print(f"导入模板失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{template_id}")
async def download_template_file(template_id: str):
    """
    下载原始模板文件（供Luckysheet直接加载）
    
    参数:
        template_id: 模板ID
    
    返回:
        Excel文件流
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 原始文件路径 FROM template_configs WHERE 模板ID = %s
        """, (template_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        file_name = row[0]
        if not file_name:
            raise HTTPException(status_code=404, detail="原始文件不存在")
        
        original_file_path = os.path.join(TEMPLATE_DIR, file_name)
        if not os.path.exists(original_file_path):
            raise HTTPException(status_code=404, detail="原始文件不存在")
        
        return FileResponse(
            original_file_path,
            filename=os.path.basename(original_file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_templates():
    """
    列出所有模板
    
    返回:
        模板列表
    """
    try:
        templates = template_engine.list_templates()
        return {
            "成功": True,
            "数据": templates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/{template_id}")
async def get_template_config(template_id: str):
    """
    获取模板配置
    
    参数:
        template_id: 模板ID
    
    返回:
        模板配置JSON
    """
    try:
        config = template_engine.load_template_config(template_id)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        return {
            "成功": True,
            "数据": config
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/{template_id}")
async def preview_template(template_id: str):
    """
    预览模板（返回完整元数据，用于Luckysheet渲染）
    
    参数:
        template_id: 模板ID
    
    返回:
        完整元数据（包含单元格、样式、合并单元格、行高列宽等）
    """
    try:
        config = template_engine.load_template_config(template_id)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        original_file_path = config.get('原始文件路径')
        original_filename = config.get('原始文件', '')
        
        if not original_file_path or not os.path.exists(original_file_path):
            original_file_path = os.path.join(TEMPLATE_DIR, original_filename)
        
        if os.path.exists(original_file_path):
            metadata = template_engine.extract_full_metadata(original_file_path)
        else:
            metadata = {
                'filename': config.get('原始文件', ''),
                'sheets': ['Sheet1'],
                'active_sheet': 0,
                'cells': [],
                'styles': {},
                'dimensions': {
                    'rows': {},
                    'columns': {},
                    'max_row': len(config.get('行数据', [])),
                    'max_column': len(config.get('列宽', []))
                },
                'merged_cells': [],
                'page_setup': config.get('页面设置', {}),
                'page_margins': config.get('页边距', {})
            }
            
            for row_data in config.get('行数据', []):
                for cell in row_data.get('单元格', []):
                    if cell.get('文本'):
                        metadata['cells'].append({
                            'r': row_data['行号'] - 1,
                            'c': cell['列号'] - 1,
                            'v': {
                                'v': cell['文本'],
                                'm': cell['文本'],
                            }
                        })
            
            for merged in config.get('合并单元格', []):
                metadata['merged_cells'].append({
                    'range': f"{merged['起始']}:{merged['结束']}",
                    'r': merged['起始行'] - 1,
                    'c': merged['起始列'] - 1,
                    'rs': merged['结束行'] - merged['起始行'] + 1,
                    'cs': merged['结束列'] - merged['起始列'] + 1
                })
        
        return {
            "成功": True,
            "数据": {
                "metadata": metadata,
                "HTML": template_engine.preview_template(config),
                "模板名称": config['模板名称'],
                "模板ID": template_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"预览错误: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/field-mapping")
async def save_field_mapping(request: FieldMappingRequest):
    """
    保存字段映射
    
    参数:
        模板ID: 模板ID
        字段名称: 字段名称
        行号: 单元格行号
        列号: 单元格列号
        数据源: 数据源（表名.字段名）
    
    返回:
        成功/失败消息
    """
    try:
        template_engine.save_field_mapping(
            request.模板ID,
            request.字段名称,
            request.行号,
            request.列号,
            request.数据源,
            request.转换单数,
            request.默认值
        )
        
        return {
            "成功": True,
            "消息": "字段映射保存成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/field-mappings/{template_id}")
async def get_field_mappings(template_id: str):
    """
    获取字段映射
    
    参数:
        template_id: 模板ID
    
    返回:
        字段映射字典
    """
    try:
        mappings = template_engine.load_field_mappings(template_id)
        return {
            "成功": True,
            "数据": mappings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fill")
async def fill_template(request: FillTemplateRequest):
    """
    自动填报数据
    
    参数:
        模板ID: 模板ID
        查询条件: 查询条件（如：{"职工ID": "xxx", "年月": "2026-05"}）
    
    返回:
        填充后的模板配置JSON
    """
    try:
        config = template_engine.load_template_config(request.模板ID)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        mappings = template_engine.load_field_mappings(request.模板ID)
        config['字段映射'] = mappings
        
        filled_config = template_engine.fill_template_data(config, request.查询条件)
        
        html = template_engine.preview_template(filled_config)
        
        return {
            "成功": True,
            "数据": {
                "配置": filled_config,
                "HTML": html
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"填报失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_template(request: FillTemplateRequest):
    """
    导出为Excel文件（基于原始文件填充数据，保证100%格式一致）
    
    参数:
        模板ID: 模板ID
        查询条件: 查询条件
    
    返回:
        Excel文件下载
    """
    try:
        config = template_engine.load_template_config(request.模板ID)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        original_file_path = config.get('原始文件路径')
        if not original_file_path or not os.path.exists(original_file_path):
            raise HTTPException(status_code=404, detail="原始文件不存在")
        
        mappings = template_engine.load_field_mappings(request.模板ID)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config['模板名称']}_{timestamp}.xlsx"
        output_path = os.path.join(EXPORT_DIR, filename)
        
        template_engine.fill_and_export_from_original(
            original_file_path, 
            mappings, 
            request.查询条件, 
            output_path
        )
        
        return FileResponse(
            output_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"导出失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export-preview/{template_id}")
async def export_preview(template_id: str):
    """
    导出预览（直接返回原始模板文件，保证100%格式一致）
    
    参数:
        template_id: 模板ID
    
    返回:
        Excel文件下载
    """
    try:
        config = template_engine.load_template_config(template_id)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        original_file_path = config.get('原始文件路径')
        original_filename = config.get('原始文件', '')
        
        if not original_file_path or not os.path.exists(original_file_path):
            original_file_path = os.path.join(TEMPLATE_DIR, original_filename)
        
        if not os.path.exists(original_file_path):
            raise HTTPException(status_code=404, detail="原始文件不存在")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config['模板名称']}_{timestamp}.xlsx"
        output_path = os.path.join(EXPORT_DIR, filename)
        
        shutil.copy2(original_file_path, output_path)
        
        return FileResponse(
            output_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    try:
        result = template_engine.delete_template(template_id)
        if not result.get("成功"):
            raise HTTPException(status_code=404, detail=result.get("消息", "删除失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
