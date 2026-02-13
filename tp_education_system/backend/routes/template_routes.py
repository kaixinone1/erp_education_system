"""
文档模板管理API - 支持多种格式模板上传、标记和填充
通用设计，支持WORD、EXCEL、PDF、HTML等格式
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, HTMLResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import psycopg2
import json
import os
import shutil
import sys

# 添加services目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.universal_placeholder_extractor import extract_fields
from services.placeholder_template_engine import PlaceholderTemplateEngine

router = APIRouter(prefix="/api/templates", tags=["templates"])


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )


@router.post("/upload")
async def upload_template(
    template_id: str = Form(...),
    template_name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...)
):
    """
    通用模板上传接口
    支持WORD(.docx)、EXCEL(.xlsx/.xls)、PDF(.pdf)、HTML(.html/.htm)格式
    自动识别占位符并生成字段配置
    """
    try:
        # 支持的文件类型
        allowed_extensions = ['.docx', '.xlsx', '.xls', '.pdf', '.html', '.htm']
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            supported = ", ".join(allowed_extensions)
            raise HTTPException(status_code=400, detail=f"不支持的文件格式。支持的格式: {supported}")

        # 创建保存目录
        save_dir = r'd:\erp_thirteen\tp_education_system\backend\templates'
        os.makedirs(save_dir, exist_ok=True)

        # 保存文件（保留原始扩展名）
        file_path = os.path.join(save_dir, f"{template_id}{file_ext}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 使用通用字段提取器提取字段
        fields = extract_fields(file_path, file_ext)

        # 保存到数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否已存在
        cursor.execute("""
            SELECT template_id FROM document_templates WHERE template_id = %s
        """, (template_id,))

        # 获取原始文件名
        file_name = file.filename

        if cursor.fetchone():
            # 更新现有模板
            cursor.execute("""
                UPDATE document_templates 
                SET template_name = %s, description = %s, file_path = %s, file_name = %s, updated_at = %s
                WHERE template_id = %s
            """, (template_name, description, file_path, file_name, datetime.now(), template_id))

            # 删除旧的字段映射
            cursor.execute("""
                DELETE FROM template_field_mappings WHERE template_id = %s
            """, (template_id,))
        else:
            # 插入新模板
            cursor.execute("""
                INSERT INTO document_templates (template_id, template_name, description, file_path, file_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (template_id, template_name, description, file_path, file_name, datetime.now(), datetime.now()))

        # 插入字段映射
        for idx, field in enumerate(fields):
            cursor.execute("""
                INSERT INTO template_field_mappings 
                (template_id, field_name, field_label, field_type, position_type, position_data, default_value, data_source, sort_order, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                template_id,
                field.get('name', f'field_{idx}'),
                field.get('label', f'字段{idx+1}'),
                field.get('field_type', 'text'),
                'coordinate',
                json.dumps(field.get('position_data', {})),
                field.get('default_value', ''),
                field.get('data_source', ''),
                idx,
                datetime.now()
            ))

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "message": "模板上传成功",
            "template_id": template_id,
            "fields_count": len(fields),
            "fields": fields
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/list")
async def list_templates():
    """
    获取模板列表
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, template_id, template_name, description, file_path, file_name, created_at, updated_at
            FROM document_templates
            ORDER BY updated_at DESC
        """)

        templates = []
        for row in cursor.fetchall():
            templates.append({
                "id": row[0],
                "template_id": row[1],
                "template_name": row[2],
                "description": row[3],
                "file_path": row[4],
                "file_name": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None
            })

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "templates": templates
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}")


@router.get("/by-name/{template_name}")
async def get_template_by_name(template_name: str):
    """
    通过模板名称查找模板
    支持模糊匹配，返回最匹配的一个
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 首先尝试精确匹配文件名
        cursor.execute("""
            SELECT id, template_id, template_name, description, file_path, file_name, created_at, updated_at
            FROM document_templates
            WHERE file_name = %s
            LIMIT 1
        """, (template_name,))
        
        row = cursor.fetchone()
        
        # 如果精确匹配失败，尝试模糊匹配
        if not row:
            cursor.execute("""
                SELECT id, template_id, template_name, description, file_path, file_name, created_at, updated_at
                FROM document_templates
                WHERE file_name LIKE %s OR template_name LIKE %s
                LIMIT 1
            """, (f'%{template_name}%', f'%{template_name}%'))
            row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"找不到模板: {template_name}")
        
        return {
            "status": "success",
            "id": row[0],
            "template_id": row[1],
            "template_name": row[2],
            "description": row[3],
            "file_path": row[4],
            "file_name": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查找模板失败: {str(e)}")


@router.get("/{template_id}")
async def get_template(template_id: str):
    """
    获取单个模板信息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, template_id, template_name, description, file_path, file_name, created_at, updated_at
            FROM document_templates
            WHERE template_id = %s
        """, (template_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        return {
            "status": "success",
            "id": row[0],
            "template_id": row[1],
            "template_name": row[2],
            "description": row[3],
            "file_path": row[4],
            "file_name": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}")


@router.get("/{template_id}/fields")
async def get_template_fields(template_id: str):
    """
    获取模板的字段映射
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT mapping_id, field_name, field_label, field_type, position_type, position_data, data_source, default_value, sort_order
            FROM template_field_mappings
            WHERE template_id = %s
            ORDER BY sort_order
        """, (template_id,))

        fields = []
        for row in cursor.fetchall():
            fields.append({
                "mapping_id": row[0],
                "field_name": row[1],
                "field_label": row[2],
                "field_type": row[3],
                "position_type": row[4],
                "position_data": row[5],
                "data_source": row[6],
                "default_value": row[7],
                "sort_order": row[8]
            })

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "template_id": template_id,
            "fields": fields
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取字段失败: {str(e)}")


@router.post("/{template_id}/fields")
async def save_template_fields(template_id: str, data: Dict[str, Any]):
    """
    保存模板的字段映射
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        fields = data.get("fields", [])

        # 删除旧的字段映射
        cursor.execute("""
            DELETE FROM template_field_mappings WHERE template_id = %s
        """, (template_id,))

        # 插入新的字段映射
        for idx, field in enumerate(fields):
            cursor.execute("""
                INSERT INTO template_field_mappings 
                (template_id, field_name, field_label, cell_ref, data_source, default_value, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                template_id,
                field.get("field_name"),
                field.get("field_label"),
                field.get("cell_ref"),
                field.get("data_source"),
                field.get("default_value"),
                idx
            ))

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "message": "字段配置保存成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.get("/{template_id}/preview")
async def preview_template(template_id: str, teacher_id: int = Query(...)):
    """
    通用预览接口 - 根据模板类型返回相应的预览
    """
    try:
        # 获取模板信息
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT file_path, file_name FROM document_templates WHERE template_id = %s
        """, (template_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="模板不存在")

        file_path, file_name = result
        file_ext = os.path.splitext(file_name)[1].lower()

        # 根据文件类型返回不同的预览
        if file_ext == '.html' or file_ext == '.htm':
            # HTML文件 - 使用 PlaceholderTemplateEngine 填充占位符
            # 获取模板ID（整数）
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM document_templates WHERE template_id = %s", (template_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not result:
                raise HTTPException(status_code=404, detail="模板不存在")
            
            template_id_int = result[0]
            
            # 使用 PlaceholderTemplateEngine 填充占位符
            engine = PlaceholderTemplateEngine(get_db_connection)
            filled_html = engine.generate_document(str(template_id_int), teacher_id)
            
            return HTMLResponse(content=filled_html)
        elif file_ext == '.docx':
            # WORD文件返回HTML预览
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from services.word_to_html import word_to_html
            from services.word_template_engine import fill_word_template
            filled_path = fill_word_template(template_id, teacher_id, get_db_connection)
            html_content = word_to_html(filled_path)
            return HTMLResponse(content=html_content)
        elif file_ext == '.pdf':
            # PDF返回图片预览
            return await preview_pdf_image(template_id, teacher_id)
        elif file_ext in ['.xlsx', '.xls']:
            # EXCEL返回HTML预览
            return await preview_excel_template(template_id, teacher_id)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file_ext}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")


@router.get("/{template_id}/preview-word")
async def preview_word_template(template_id: str, teacher_id: int = Query(...)):
    """
    预览填充后的WORD模板
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.word_template_engine import fill_word_template

        # 生成填充后的WORD
        output_path = fill_word_template(template_id, teacher_id, get_db_connection)

        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="文档生成失败")

        # 返回文件 - 使用生成的文件名（已经是"模板名称+教师姓名"格式）
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=os.path.basename(output_path)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")


@router.get("/{template_id}/preview-html")
async def preview_word_html(template_id: str, teacher_id: int = Query(...)):
    """
    将填充后的WORD模板转换为HTML预览
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.word_to_html import word_to_html

        # 先生成填充后的WORD
        from services.word_template_engine import fill_word_template
        filled_path = fill_word_template(template_id, teacher_id, get_db_connection)

        if not os.path.exists(filled_path):
            raise HTTPException(status_code=500, detail="文档生成失败")

        # 转换为HTML
        html_content = word_to_html(filled_path)

        return HTMLResponse(content=html_content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML预览生成失败: {str(e)}")


@router.get("/{template_id}/preview-pdf")
async def preview_pdf_image(
    template_id: str,
    marks: str = Query("[]"),
    selected_x: int = Query(None),
    selected_y: int = Query(None),
    selected_page: int = Query(1),
    page: int = Query(1)
):
    """
    将PDF模板转换为图片预览，支持标记和多页
    """
    try:
        import json
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.pdf_handler import pdf_page_to_image, generate_preview_with_marks, get_pdf_page_count

        # 获取模板文件路径
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT file_path FROM document_templates WHERE template_id = %s
        """, (template_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")

        file_path = row[0]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 检查是否是PDF
        if not file_path.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="该模板不是PDF格式")

        # 获取PDF总页数
        total_pages = get_pdf_page_count(file_path)

        # 解析标记
        marks_list = json.loads(marks) if marks else []
        selected_mark = None
        if selected_x is not None and selected_y is not None:
            selected_mark = {"x": selected_x, "y": selected_y, "page": selected_page}

        # 生成带标记的预览图
        if marks_list or selected_mark:
            img_data = generate_preview_with_marks(file_path, marks_list, selected_mark, page=page)
        else:
            img_data = pdf_page_to_image(file_path, page=page)

        return {"image": img_data, "total_pages": total_pages, "current_page": page}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF预览生成失败: {str(e)}")


@router.get("/{template_id}/preview-excel")
async def preview_excel_template(template_id: str, teacher_id: int = Query(...)):
    """
    预览填充后的Excel模板
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.excel_engine import fill_excel_from_template

        # 生成填充后的Excel
        output_path = fill_excel_from_template(template_id, teacher_id, get_db_connection)

        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Excel生成失败")

        # 返回文件 - 使用生成的文件名（已经是"模板名称+教师姓名"格式）
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(output_path)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")


@router.get("/{template_id}/extract-fields")
async def extract_template_fields(template_id: str):
    """
    自动提取模板中的字段
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.field_extractor import extract_pdf_fields
        from services.field_matcher import match_template_fields

        # 获取模板文件路径
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT file_path FROM document_templates WHERE template_id = %s
        """, (template_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")

        file_path = row[0]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 提取PDF字段
        template_fields = extract_pdf_fields(file_path)

        # 匹配数据源
        matches = match_template_fields(template_fields)

        return {
            "status": "success",
            "template_id": template_id,
            "matches": matches
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"字段提取失败: {str(e)}")


@router.post("/{template_id}/html-fields")
async def save_html_template_fields(template_id: str, data: Dict[str, Any]):
    """
    保存HTML模板的字段配置
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        fields = data.get("fields", [])

        # 删除旧的字段映射
        cursor.execute("""
            DELETE FROM template_field_mappings WHERE template_id = %s
        """, (template_id,))

        # 插入新的字段映射
        for idx, field in enumerate(fields):
            cursor.execute("""
                INSERT INTO template_field_mappings 
                (template_id, field_name, field_label, field_type, position_type, position_data, default_value, data_source, sort_order, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                template_id,
                field.get("field_name", f"field_{idx}"),
                field.get("field_label", f"字段{idx+1}"),
                field.get("field_type", "text"),
                field.get("position_type", "coordinate"),
                json.dumps(field.get("position_data", {})),
                field.get("default_value", ""),
                field.get("data_source", ""),
                field.get("sort_order", idx),
                datetime.now()
            ))

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "message": "字段配置保存成功",
            "fields_count": len(fields)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.post("/{template_id}/generate-form")
async def generate_html_form(template_id: str):
    """
    根据字段配置生成可填写的HTML表单
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取模板信息
        cursor.execute("""
            SELECT file_path, file_name FROM document_templates WHERE template_id = %s
        """, (template_id,))
        template_row = cursor.fetchone()

        if not template_row:
            raise HTTPException(status_code=404, detail="模板不存在")

        file_path, file_name = template_row

        # 获取字段配置
        cursor.execute("""
            SELECT field_name, field_label, position_data
            FROM template_field_mappings
            WHERE template_id = %s
            ORDER BY sort_order
        """, (template_id,))

        fields = []
        for row in cursor.fetchall():
            fields.append({
                "field_name": row[0],
                "field_label": row[1],
                "position_data": row[2]
            })

        cursor.close()
        conn.close()

        # 读取原始HTML
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 添加表单样式
        style_tag = soup.find('style')
        if style_tag:
            form_styles = """
/* 表单输入框样式 */
.html-form-input {
    width: 95%;
    height: 90%;
    border: 1px solid #409eff;
    padding: 2px 5px;
    font-size: inherit;
    font-family: inherit;
    background: #fff;
    box-sizing: border-box;
}
.html-form-input:focus {
    border-color: #1890ff;
    outline: none;
}
"""
            style_tag.string = style_tag.string + form_styles

        # 获取所有表格单元格
        tables = soup.find_all('table')
        cell_index = 0

        for table in tables:
            cells = table.find_all(['td', 'th'])
            for cell in cells:
                # 检查是否有对应的字段
                field = next((f for f in fields if f.get("position_data", {}).get("cellIndex") == cell_index), None)

                if field:
                    # 清空单元格并添加输入框
                    cell.clear()
                    input_tag = soup.new_tag('input')
                    input_tag['type'] = 'text'
                    input_tag['name'] = field["field_name"]
                    input_tag['id'] = field["field_name"]
                    input_tag['class'] = 'html-form-input'
                    input_tag['placeholder'] = field["field_label"]
                    cell.append(input_tag)

                cell_index += 1

        # 保存生成的HTML
        form_path = file_path.replace('.html', '_form.html')
        with open(form_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        return {
            "status": "success",
            "message": "表单生成成功",
            "form_path": form_path,
            "fields_count": len(fields)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成表单失败: {str(e)}")


@router.post("/{template_id}/regions")
async def save_template_regions(template_id: str, data: Dict[str, Any]):
    """
    保存模板的区域边框设置
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先删除该模板该页的旧区域设置
        cursor.execute("""
            DELETE FROM template_regions 
            WHERE template_id = %s AND page = %s
        """, (template_id, data.get('page', 1)))
        
        # 插入新区域设置
        for region in data.get('regions', []):
            cursor.execute("""
                INSERT INTO template_regions 
                (template_id, region_id, name, page, x0, y0, x1, y1)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                template_id,
                region['id'],
                region['name'],
                data.get('page', 1),
                region['bounds']['x0'],
                region['bounds']['y0'],
                region['bounds']['x1'],
                region['bounds']['y1']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "区域边框保存成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存区域边框失败: {str(e)}")


@router.get("/{template_id}/regions")
async def get_template_regions(template_id: str, page: int = Query(1)):
    """
    获取模板的区域边框设置
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT region_id, name, x0, y0, x1, y1 
            FROM template_regions 
            WHERE template_id = %s AND page = %s
            ORDER BY region_id
        """, (template_id, page))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        regions = []
        for row in rows:
            regions.append({
                "id": row[0],
                "name": row[1],
                "bounds": {
                    "x0": row[2],
                    "y0": row[3],
                    "x1": row[4],
                    "y1": row[5]
                },
                "page": page
            })
        
        return {
            "status": "success",
            "template_id": template_id,
            "page": page,
            "regions": regions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取区域边框失败: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """
    删除模板
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取模板文件路径
        cursor.execute("""
            SELECT file_path FROM document_templates WHERE template_id = %s
        """, (template_id,))

        row = cursor.fetchone()
        if row:
            file_path = row[0]
            # 删除文件
            if os.path.exists(file_path):
                os.remove(file_path)

        # 删除数据库记录（级联删除字段映射）
        cursor.execute("""
            DELETE FROM document_templates WHERE template_id = %s
        """, (template_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "message": "模板删除成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/{template_id}/content")
async def get_template_content(template_id: str):
    """
    获取模板的HTML内容（原始内容，未填充数据）
    用于ReportView组件渲染
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取模板信息
        cursor.execute("""
            SELECT file_path, file_name FROM document_templates WHERE template_id = %s
        """, (template_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        file_path, file_name = row
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="模板文件不存在")
        
        # 根据文件类型返回内容
        file_ext = os.path.splitext(file_name)[1].lower()
        
        if file_ext in ['.html', '.htm']:
            # 直接读取HTML文件，尝试多种编码
            content = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # 如果所有编码都失败，使用二进制读取然后忽略错误
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            return HTMLResponse(content=content)
        
        elif file_ext == '.docx':
            # 将WORD转换为HTML
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from services.word_to_html import word_to_html
            content = word_to_html(file_path)
            return HTMLResponse(content=content)
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file_ext}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板内容失败: {str(e)}")


# ==================== A3纸四区域检测API ====================

@router.get("/{template_id}/a3-regions")
async def detect_a3_regions_api(template_id: str, page: int = Query(1, description="页码")):
    """
    检测A3纸的4个编辑区域
    返回区域边界和四角坐标，用于前端显示和调整
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.a3_region_detector import A3RegionDetector

        # 获取模板文件路径
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT file_path FROM document_templates WHERE template_id = %s
        """, (template_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")

        file_path = row[0]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 检测A3区域
        detector = A3RegionDetector(file_path)
        preview_data = detector.get_region_preview_data(page_num=page)

        if not preview_data:
            return {
                "status": "success",
                "is_a3": False,
                "message": "该PDF不是A3格式，无需分区处理"
            }

        return {
            "status": "success",
            "is_a3": True,
            "page_width": preview_data["page_width"],
            "page_height": preview_data["page_height"],
            "regions": preview_data["regions"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"区域检测失败: {str(e)}")


@router.post("/{template_id}/a3-regions/extract")
async def extract_fields_from_regions(template_id: str, data: Dict[str, Any]):
    """
    从指定的A3区域中提取字段
    
    请求体:
    {
        "page": 1,
        "regions": [
            {
                "id": 1,
                "bounds": {"x0": 85, "y0": 85, "x1": 595, "y1": 420}
            }
        ]
    }
    """
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.a3_region_detector import A3RegionDetector, Region

        # 获取模板文件路径
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT file_path FROM document_templates WHERE template_id = %s
        """, (template_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")

        file_path = row[0]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        page_num = data.get("page", 1)
        regions_data = data.get("regions", [])

        detector = A3RegionDetector(file_path)
        all_fields = []

        for region_data in regions_data:
            region_id = region_data.get("id")
            bounds = region_data.get("bounds", {})

            # 创建Region对象
            region = Region(
                id=region_id,
                name=f"区域{region_id}",
                page=page_num,
                x0=bounds.get("x0", 0),
                y0=bounds.get("y0", 0),
                x1=bounds.get("x1", 0),
                y1=bounds.get("y1", 0),
                corners=[]
            )

            # 从区域提取字段
            fields = detector.extract_fields_from_region(region, page_num)
            all_fields.extend(fields)

        return {
            "status": "success",
            "template_id": template_id,
            "page": page_num,
            "fields_count": len(all_fields),
            "fields": all_fields
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"字段提取失败: {str(e)}")
