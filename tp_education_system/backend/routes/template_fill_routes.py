"""
模板填充API路由 - 提供模板填充和导出功能
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional
import os
import sys
import psycopg2

# 数据库连接函数
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )

# 延迟导入模板引擎，避免循环导入
def get_template_engine():
    from services.template_engine import TemplateEngine
    return TemplateEngine(get_db_connection)

router = APIRouter(prefix="/api/template-fill", tags=["template-fill"])


@router.post("/generate")
async def generate_document(request: Dict[str, Any]):
    """
    生成填充后的文档
    
    请求参数:
    - template_id: 模板ID
    - business_id: 业务对象ID（如教师ID）
    - override_data: 可选，覆盖数据（如表单填写的数据）
    """
    try:
        template_id = request.get("template_id")
        business_id = request.get("business_id")
        override_data = request.get("override_data", {})
        
        if not template_id or not business_id:
            raise HTTPException(
                status_code=400, 
                detail="模板ID和业务对象ID不能为空"
            )
        
        # 获取模板路径
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM document_templates WHERE template_id = %s", (template_id,))
        template_row = cursor.fetchone()
        if not template_row:
            raise HTTPException(status_code=404, detail="模板不存在")
        template_path = template_row[0]
        cursor.close()
        conn.close()
        
        # 获取教师数据
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, id_card, archive_birth_date, ethnicity,
                   native_place, work_start_date, contact_phone
            FROM teacher_basic_info WHERE id = %s
        """, (business_id,))
        teacher_row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not teacher_row:
            raise HTTPException(status_code=404, detail="教师不存在")
        
        teacher_data = {
            "id": teacher_row[0],
            "name": teacher_row[1] or "",
            "id_card": teacher_row[2] or "",
            "archive_birth_date": str(teacher_row[3]) if teacher_row[3] else "",
            "ethnicity": teacher_row[4] or "",
            "native_place": teacher_row[5] or "",
            "work_start_date": str(teacher_row[6]) if teacher_row[6] else "",
            "contact_phone": teacher_row[7] or ""
        }
        
        # 合并数据
        fill_data = {**teacher_data, **override_data}
        
        # 使用自动分析器填充文档
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.auto_template_analyzer import AutoTemplateAnalyzer
        
        output_dir = r'd:\erp_thirteen\tp_education_system\backend\uploads\generated'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{template_id}_{business_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.docx')
        
        AutoTemplateAnalyzer.auto_fill_template(template_path, fill_data, output_path)
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="文档生成失败")
        
        # 返回文件
        filename = os.path.basename(output_path)
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成文档失败: {str(e)}")


@router.get("/preview")
async def preview_document(
    template_id: str = Query(..., description="模板ID"),
    business_id: int = Query(..., description="业务对象ID")
):
    """
    预览模板填充效果
    
    使用示例数据填充模板，用于预览效果
    """
    try:
        # 延迟初始化模板引擎
        template_engine = get_template_engine()
        
        # 调用模板引擎生成预览文档
        output_path = template_engine.preview_template(
            template_id=template_id,
            business_id=business_id
        )
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="预览生成失败")
        
        # 返回文件
        filename = os.path.basename(output_path)
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")


@router.get("/template-config/{template_id}")
async def get_template_config(template_id: str):
    """
    获取模板配置信息
    """
    try:
        template_engine = get_template_engine()
        config = template_engine.get_template_config(template_id)
        return {
            "status": "success",
            "data": config
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板配置失败: {str(e)}")
