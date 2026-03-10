"""
通用模板管理路由
支持Word/Excel模板上传、占位符提取、字段映射配置、数据导出
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
import re
import tempfile

# 导入Excel转PDF工具
from .excel_to_pdf import convert_excel_to_pdf

router = APIRouter(prefix="/api/universal-templates", tags=["通用模板"])

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

TEMPLATES_DIR = r"d:\erp_thirteen\tp_education_system\backend\universal_templates"

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def extract_placeholders_from_docx(file_path: str) -> list:
    """从Word文档提取占位符"""
    try:
        from docx import Document
        import re
        
        placeholders = []
        
        doc = Document(file_path)
        
        for para in doc.paragraphs:
            found = re.findall(r'\{\{([^}]+)\}\}', para.text)
            for f in found:
                if f not in placeholders:
                    placeholders.append(f)
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    found = re.findall(r'\{\{([^}]+)\}\}', cell.text)
                    for f in found:
                        if f not in placeholders:
                            placeholders.append(f)
        
        return placeholders
    except Exception as e:
        print(f"提取Word占位符失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_page_info_from_docx(file_path: str) -> dict:
    """从Word文档提取页面设置信息"""
    try:
        from docx import Document
        
        doc = Document(file_path)
        section = doc.sections[0]
        
        # 页面尺寸（毫米）
        page_width = section.page_width.mm
        page_height = section.page_height.mm
        
        # 判断页面大小
        if page_width >= 400:
            page_size = "A3"
        elif page_width >= 280:
            page_size = "A4"
        else:
            page_size = "其他"
        
        # 判断横向/纵向
        if page_width > page_height:
            orientation = "横向"
        else:
            orientation = "纵向"
        
        # 页边距（毫米）
        margin_top = section.top_margin.mm
        margin_bottom = section.bottom_margin.mm
        margin_left = section.left_margin.mm
        margin_right = section.right_margin.mm
        
        return {
            "page_size": page_size,
            "orientation": orientation,
            "page_width_mm": round(page_width, 1),
            "page_height_mm": round(page_height, 1),
            "margin_top_mm": round(margin_top, 1),
            "margin_bottom_mm": round(margin_bottom, 1),
            "margin_left_mm": round(margin_left, 1),
            "margin_right_mm": round(margin_right, 1)
        }
    except Exception as e:
        print(f"提取页面信息失败: {e}")
        return {
            "page_size": "A4",
            "orientation": "纵向",
            "page_width_mm": 210,
            "page_height_mm": 297
        }


def extract_placeholders_from_xlsx(file_path: str) -> list:
    """从Excel文档提取占位符"""
    import re
    
    file_ext = file_path.lower().split('.')[-1]
    
    try:
        if file_ext == 'xlsx':
            from openpyxl import load_workbook
            wb = load_workbook(file_path, data_only=False)
            placeholders = []
            
            for ws in wb.worksheets:
                for row in ws.iter_rows():
                    for cell in row:
                        if cell.value and isinstance(cell.value, str):
                            found = re.findall(r'\{\{([^}]+)\}\}', cell.value)
                            for f in found:
                                if f not in placeholders:
                                    placeholders.append(f)
            
            return placeholders
        elif file_ext == 'xls':
            import xlrd
            wb = xlrd.open_workbook(file_path)
            placeholders = []
            
            for sheet in wb.sheets():
                for row_idx in range(sheet.nrows):
                    for col_idx in range(sheet.ncols):
                        cell_value = sheet.cell(row_idx, col_idx).value
                        if cell_value and isinstance(cell_value, str):
                            found = re.findall(r'\{\{([^}]+)\}\}', cell_value)
                            for f in found:
                                if f not in placeholders:
                                    placeholders.append(f)
            
            return placeholders
        else:
            return []
    except Exception as e:
        print(f"提取Excel占位符失败: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.post("/upload")
async def upload_template(
    file: UploadFile = File(...),
    template_name: str = Form(...),
    placeholder_config: str = Form("{}"),
    activation_type: str = Form("status_change"),
    activation_config: str = Form("{}")
):
    """
    上传通用模板
    自动提取文件中的占位符
    """
    try:
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ['doc', 'docx', 'xls', 'xlsx']:
            raise HTTPException(status_code=400, detail="只支持.doc/.docx/.xls/.xlsx格式的文件")
        
        template_id = file.filename.rsplit('.', 1)[0]
        
        file_path = os.path.join(TEMPLATES_DIR, file.filename)
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # 提取占位符和页面设置
        if file_ext in ['doc', 'docx']:
            placeholders = extract_placeholders_from_docx(file_path)
            page_info = extract_page_info_from_docx(file_path)
        else:
            placeholders = extract_placeholders_from_xlsx(file_path)
            page_info = {
                "page_size": "A4",
                "orientation": "纵向",
                "page_width_mm": 210,
                "page_height_mm": 297
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            config_json = json.loads(placeholder_config) if placeholder_config else {}
            activation_config_json = json.loads(activation_config) if activation_config else {}
        except:
            config_json = {}
            activation_config_json = {}
        
        cursor.execute("""
            INSERT INTO universal_templates (template_id, template_name, file_path, file_type, placeholders, placeholder_config, page_info, activation_type, activation_config)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (template_id) DO UPDATE SET
                template_name = EXCLUDED.template_name,
                file_path = EXCLUDED.file_path,
                file_type = EXCLUDED.file_type,
                placeholders = EXCLUDED.placeholders,
                placeholder_config = EXCLUDED.placeholder_config,
                page_info = EXCLUDED.page_info,
                activation_type = EXCLUDED.activation_type,
                activation_config = EXCLUDED.activation_config,
                updated_at = CURRENT_TIMESTAMP
        """, (template_id, template_name, file_path, file_ext, json.dumps(placeholders), json.dumps(config_json), json.dumps(page_info), activation_type, json.dumps(activation_config_json)))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "模板上传成功",
            "data": {
                "template_id": template_id,
                "template_name": template_name,
                "placeholders": placeholders,
                "placeholder_count": len(placeholders)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"上传模板失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_templates(activation_type: str = None):
    """获取模板列表，支持按激活方式筛选"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if activation_type:
            cursor.execute("""
                SELECT template_id, template_name, file_type, placeholders, placeholder_config, 
                       activation_type, activation_config, created_at, updated_at
                FROM universal_templates
                WHERE activation_type = %s
                ORDER BY updated_at DESC
            """, (activation_type,))
        else:
            cursor.execute("""
                SELECT template_id, template_name, file_type, placeholders, placeholder_config, 
                       activation_type, activation_config, created_at, updated_at
                FROM universal_templates
                ORDER BY updated_at DESC
            """)
        
        rows = cursor.fetchall()
        
        for row in rows:
            if row['placeholders'] and isinstance(row['placeholders'], str):
                row['placeholders'] = json.loads(row['placeholders'])
            if row['placeholder_config'] and isinstance(row['placeholder_config'], str):
                row['placeholder_config'] = json.loads(row['placeholder_config'])
            if row['activation_config'] and isinstance(row['activation_config'], str):
                row['activation_config'] = json.loads(row['activation_config'])
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": rows}
        
    except Exception as e:
        print(f"获取模板列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{template_id}/refresh-placeholders")
async def refresh_placeholders(template_id: str):
    """重新从模板文件提取占位符"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, template_id, template_name, file_path, file_type, placeholders
            FROM universal_templates WHERE template_id = %s
        """, (template_id,))
        
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="模板不存在")
        
        file_path = row['file_path']
        file_type = row['file_type']
        
        if not os.path.exists(file_path):
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="模板文件不存在")
        
        if file_type in ['doc', 'docx']:
            placeholders = extract_placeholders_from_docx(file_path)
        elif file_type in ['xls', 'xlsx']:
            placeholders = extract_placeholders_from_xlsx(file_path)
        else:
            placeholders = []
        
        cursor.execute("""
            UPDATE universal_templates 
            SET placeholders = %s, updated_at = CURRENT_TIMESTAMP
            WHERE template_id = %s
        """, (json.dumps(placeholders), template_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"重新提取成功，共 {len(placeholders)} 个占位符",
            "data": {
                "template_id": template_id,
                "placeholders": placeholders
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"重新提取占位符失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}")
async def get_template(template_id: str, refresh: bool = Query(False, description="是否重新提取占位符")):
    """获取模板详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, template_id, template_name, file_path, file_type, placeholders, placeholder_config, page_info, 
                   activation_type, activation_config, created_at, updated_at
            FROM universal_templates WHERE template_id = %s
        """, (template_id,))
        
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="模板不存在")
        
        placeholders = row['placeholders']
        if refresh or not placeholders:
            file_path = row['file_path']
            file_type = row['file_type']
            
            if os.path.exists(file_path):
                if file_type == 'docx':
                    placeholders = extract_placeholders_from_docx(file_path)
                elif file_type == 'xlsx':
                    placeholders = extract_placeholders_from_xlsx(file_path)
                else:
                    placeholders = []
                
                cursor.execute("""
                    UPDATE universal_templates SET placeholders = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE template_id = %s
                """, (json.dumps(placeholders), template_id))
                conn.commit()
                
                row['placeholders'] = placeholders
            else:
                row['placeholders'] = []
        else:
            row['placeholders'] = json.loads(placeholders) if isinstance(placeholders, str) else placeholders
        
        if row['placeholder_config']:
            row['placeholder_config'] = json.loads(row['placeholder_config']) if isinstance(row['placeholder_config'], str) else row['placeholder_config']
        else:
            row['placeholder_config'] = {}
        
        if row['page_info']:
            row['page_info'] = json.loads(row['page_info']) if isinstance(row['page_info'], str) else row['page_info']
        else:
            row['page_info'] = {
                "page_size": "A4",
                "orientation": "纵向",
                "page_width_mm": 210,
                "page_height_mm": 297
            }
        
        if row['activation_config']:
            row['activation_config'] = json.loads(row['activation_config']) if isinstance(row['activation_config'], str) else row['activation_config']
        else:
            row['activation_config'] = {}
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": row}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取模板详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """删除模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取文件路径
        cursor.execute("SELECT file_path FROM universal_templates WHERE template_id = %s", (template_id,))
        row = cursor.fetchone()
        
        if row and os.path.exists(row[0]):
            os.remove(row[0])
        
        # 删除数据库记录
        cursor.execute("DELETE FROM universal_templates WHERE template_id = %s", (template_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "message": "模板已删除"}
        
    except Exception as e:
        print(f"删除模板失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}/config")
async def update_template_config(template_id: str, config: dict):
    """更新模板的占位符配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE universal_templates 
            SET placeholder_config = %s, updated_at = CURRENT_TIMESTAMP
            WHERE template_id = %s
        """, (json.dumps(config), template_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "message": "配置已更新"}
        
    except Exception as e:
        print(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}/activation")
async def update_template_activation(template_id: str, activation: dict):
    """更新模板的激活方式配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        activation_type = activation.get('activation_type', 'status_change')
        activation_config = activation.get('activation_config', {})
        
        cursor.execute("""
            UPDATE universal_templates 
            SET activation_type = %s, activation_config = %s, updated_at = CURRENT_TIMESTAMP
            WHERE template_id = %s
        """, (activation_type, json.dumps(activation_config), template_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "message": "激活方式已更新"}
        
    except Exception as e:
        print(f"更新激活方式失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 教师搜索API ============

@router.get("/teachers/search")
async def search_teachers(q: str = Query(..., description="搜索关键词")):
    """搜索教师（按姓名或身份证号）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 支持姓名或身份证号搜索
        cursor.execute("""
            SELECT id, name, id_card, employment_status
            FROM teacher_basic_info
            WHERE name ILIKE %s OR id_card ILIKE %s
            ORDER BY name
            LIMIT 20
        """, (f'%{q}%', f'%{q}%'))
        
        teachers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": teachers}
        
    except Exception as e:
        print(f"搜索教师失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"搜索教师失败: {str(e)}")


# ============ 数据获取和填充功能 ============

def get_field_mappings():
    """获取字段映射配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT placeholder, table_name, field_name, condition_field
            FROM universal_template_field_mapping
            WHERE is_active = true
        """)
        
        mappings = {}
        for row in cursor.fetchall():
            mappings[row['placeholder']] = {
                'table': row['table_name'],
                'field': row['field_name'],
                'condition': row['condition_field'] or 'teacher_id'
            }
        
        cursor.close()
        conn.close()
        return mappings
    except Exception as e:
        print(f"获取字段映射失败: {e}")
        return {}


def get_teacher_data(teacher_id: int, field_mappings: dict) -> dict:
    """根据字段映射获取教师数据"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    data = {}
    
    # 按表分组
    tables_fields = {}
    for placeholder, mapping in field_mappings.items():
        table = mapping.get('table')
        field = mapping.get('field')
        condition = mapping.get('condition', 'teacher_id')
        if table and field:
            if table not in tables_fields:
                tables_fields[table] = []
            tables_fields[table].append((placeholder, field, condition))
    
    # 查询每个表
    for table_name, fields in tables_fields.items():
        try:
            field_names = [f[1] for f in fields]
            placeholders_list = [f[0] for f in fields]
            condition_field = fields[0][2]
            
            fields_str = ', '.join([f'"{f}"' for f in field_names])
            sql = f'SELECT {fields_str} FROM {table_name} WHERE "{condition_field}" = %s'
            
            cursor.execute(sql, (teacher_id,))
            row = cursor.fetchone()
            
            if row:
                for placeholder, field, _ in fields:
                    data[placeholder] = row.get(field, '')
        except Exception as e:
            print(f"查询表 {table_name} 失败: {e}")
    
    cursor.close()
    conn.close()
    return data


def get_teacher_data_by_config(teacher_id: int, placeholder_config: dict) -> dict:
    """根据模板占位符配置获取教师数据"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    data = {}
    
    tables_fields = {}
    for placeholder, config in placeholder_config.items():
        table = config.get('表名') or config.get('table')
        field = config.get('字段名') or config.get('field')
        if not table or not field:
            continue
        
        aggregate_func = config.get('聚合函数') or config.get('aggregate_func', '')
        filter_condition = config.get('过滤条件') or config.get('filter_condition', '')
        
        if table not in tables_fields:
            tables_fields[table] = []
        tables_fields[table].append({
            'placeholder': placeholder,
            'field': field,
            'condition_field': config.get('条件字段', 'teacher_id'),
            'aggregate_func': aggregate_func,
            'filter_condition': filter_condition
        })
    
    for table_name, fields_config in tables_fields.items():
        try:
            if not re.match(r'^[a-zA-Z_]+$', table_name):
                continue
            
            for fc in fields_config:
                placeholder = fc['placeholder']
                field = fc['field']
                condition_field = fc['condition_field']
                aggregate_func = fc['aggregate_func']
                filter_condition = fc['filter_condition']
                
                if aggregate_func:
                    field_expr = f"{aggregate_func}(\"{field}\")"
                else:
                    field_expr = f'"{field}"'
                
                sql = f'SELECT {field_expr} FROM {table_name}'
                params = []
                
                where_clauses = []
                if condition_field:
                    where_clauses.append(f'"{condition_field}" = %s')
                    params.append(teacher_id)
                
                if filter_condition:
                    where_clauses.append(f"({filter_condition})")
                
                if where_clauses:
                    sql += ' WHERE ' + ' AND '.join(where_clauses)
                
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if row and row[field_expr if not aggregate_func else aggregate_func + '(' + field + ')']:
                    result_value = row[field_expr if not aggregate_func else aggregate_func + '(' + field + ')']
                    if aggregate_func and result_value is not None:
                        data[placeholder] = str(result_value)
                    elif not aggregate_func:
                        data[placeholder] = result_value
                    
        except Exception as e:
            print(f"查询表 {table_name} 失败: {e}")
    
    cursor.close()
    conn.close()
    return data


def fill_docx_template(template_path: str, output_path: str, data: dict):
    """填充Word模板"""
    from docx import Document
    
    doc = Document(template_path)
    
    # 替换段落中的占位符
    for para in doc.paragraphs:
        for placeholder, value in data.items():
            if f'{{{{{placeholder}}}}}' in para.text:
                for run in para.runs:
                    placeholder_pattern = '{{' + placeholder + '}}'
                    if placeholder_pattern in run.text:
                        run.text = run.text.replace(placeholder_pattern, str(value) if value is not None else '')
    
    # 替换表格中的占位符
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for placeholder, value in data.items():
                    placeholder_pattern = '{{' + placeholder + '}}'
                    if placeholder_pattern in cell.text:
                        for para in cell.paragraphs:
                            for run in para.runs:
                                if placeholder_pattern in run.text:
                                    run.text = run.text.replace(placeholder_pattern, str(value) if value is not None else '')
    
    doc.save(output_path)


def fill_xlsx_template(template_path: str, output_path: str, data: dict):
    """填充Excel模板（支持 .xlsx 和 .xls 格式）"""
    file_ext = template_path.lower().split('.')[-1]
    
    if file_ext == 'xlsx':
        from openpyxl import load_workbook
        wb = load_workbook(template_path)
        
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        for placeholder, value in data.items():
                            # 占位符格式: {{placeholder}}
                            placeholder_pattern = '{{' + placeholder + '}}'
                            if placeholder_pattern in cell.value:
                                cell.value = cell.value.replace(placeholder_pattern, str(value) if value is not None else '')
        
        wb.save(output_path)
    elif file_ext == 'xls':
        import xlrd
        from xlwt import Workbook
        
        # 读取旧格式
        rb = xlrd.open_workbook(template_path)
        wb = Workbook()
        
        for sheet_idx in range(rb.nsheets):
            rs = rb.sheet_by_index(sheet_idx)
            ws = wb.add_sheet(rs.name)
            
            for row_idx in range(rs.nrows):
                for col_idx in range(rs.ncols):
                    cell_value = rs.cell_value(row_idx, col_idx)
                    if isinstance(cell_value, str):
                        for placeholder, value in data.items():
                            # 占位符格式: {{placeholder}}
                            placeholder_pattern = '{{' + placeholder + '}}'
                            if placeholder_pattern in cell_value:
                                cell_value = cell_value.replace(placeholder_pattern, str(value) if value is not None else '')
                    ws.write(row_idx, col_idx, cell_value)
        
        wb.save(output_path)
    else:
        raise ValueError(f"不支持的Excel格式: {file_ext}")


def convert_docx_to_pdf(docx_path: str, pdf_path: str):
    """将Word文档转换为PDF"""
    try:
        from docx2pdf import convert
        convert(docx_path, pdf_path)
        return True
    except Exception as e:
        print(f"Word转PDF失败: {e}")
        return False


# ============ Excel数据API ============

@router.get("/{template_id}/excel-data")
async def get_excel_data(template_id: str):
    """获取Excel模板的数据（用于手工编辑）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT template_id, file_path, file_type
            FROM universal_templates WHERE template_id = %s
        """, (template_id,))
        
        template = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        file_path = template['file_path']
        file_type = template['file_type']
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="模板文件不存在")
        
        # 读取Excel数据
        data = []
        if file_type == 'xlsx':
            from openpyxl import load_workbook
            wb = load_workbook(file_path, data_only=True)
            ws = wb.active
            for row in ws.iter_rows():
                row_data = []
                for cell in row:
                    value = cell.value if cell.value is not None else ""
                    row_data.append(str(value))
                data.append(row_data)
        elif file_type == 'xls':
            import xlrd
            wb = xlrd.open_workbook(file_path)
            ws = wb.sheet_by_index(0)
            for row_idx in range(ws.nrows):
                row_data = []
                for col_idx in range(ws.ncols):
                    value = ws.cell_value(row_idx, col_idx)
                    row_data.append(str(value) if value is not None else "")
                data.append(row_data)
        
        return {"status": "success", "data": data}
        
    except Exception as e:
        print(f"获取Excel数据失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取Excel数据失败: {str(e)}")


@router.post("/{template_id}/save-excel")
async def save_excel_data(template_id: str, request: dict):
    """保存Excel数据（手工编辑后）"""
    try:
        data = request.get('data', [])
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT template_id, file_path, file_type
            FROM universal_templates WHERE template_id = %s
        """, (template_id,))
        
        template = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        file_path = template['file_path']
        file_type = template['file_type']
        
        # 保存Excel数据
        if file_type == 'xlsx':
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            
            for row_idx, row in enumerate(data):
                for col_idx, cell_value in enumerate(row):
                    ws.cell(row=row_idx + 1, column=col_idx + 1, value=cell_value)
            
            wb.save(file_path)
        elif file_type == 'xls':
            from xlwt import Workbook
            wb = Workbook()
            ws = wb.add_sheet('Sheet1')
            
            for row_idx, row in enumerate(data):
                for col_idx, cell_value in enumerate(row):
                    ws.write(row_idx, col_idx, cell_value)
            
            wb.save(file_path)
        
        return {"status": "success", "message": "保存成功"}
        
    except Exception as e:
        print(f"保存Excel数据失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"保存Excel数据失败: {str(e)}")


# ============ 导出API ============

@router.get("/{template_id}/export")
async def export_template(
    template_id: str,
    teacher_id: int = Query(..., description="教师ID"),
    teacher_name: str = Query('', description="教师姓名")
):
    """导出填充后的模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT template_id, template_name, file_path, file_type, placeholder_config
            FROM universal_templates WHERE template_id = %s
        """, (template_id,))
        
        template = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        placeholder_config = {}
        if template.get('placeholder_config'):
            placeholder_config = json.loads(template['placeholder_config']) if isinstance(template['placeholder_config'], str) else template['placeholder_config']
        
        if placeholder_config:
            teacher_data = get_teacher_data_by_config(teacher_id, placeholder_config)
        else:
            field_mappings = get_field_mappings()
            teacher_data = get_teacher_data(teacher_id, field_mappings)
        
        if not teacher_name:
            if '姓名' in teacher_data:
                teacher_name = teacher_data.get('姓名', '')
            else:
                teacher_name = str(teacher_id)
        
        template_path = template['file_path']
        file_ext = template['file_type']
        
        output_filename = f"{template['template_name']}_{teacher_name}_已填充.{file_ext}"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)
        
        if file_ext == 'docx':
            fill_docx_template(template_path, output_path, teacher_data)
        else:
            fill_xlsx_template(template_path, output_path, teacher_data)
        
        return FileResponse(
            output_path,
            filename=output_filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document' if file_ext == 'docx' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"导出失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/{template_id}/preview")
async def preview_template(
    template_id: str,
    teacher_id: int = Query(..., description="教师ID")
):
    """预览填充后的模板 - 生成临时文件并返回下载URL"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT template_id, template_name, file_path, file_type, placeholder_config, placeholders, page_info
            FROM universal_templates WHERE template_id = %s
        """, (template_id,))
        
        template = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        file_ext = template['file_type']
        template_placeholders = json.loads(template['placeholders']) if template['placeholders'] else []
        
        # 获取教师数据
        placeholder_config = {}
        if template.get('placeholder_config'):
            placeholder_config = json.loads(template['placeholder_config']) if isinstance(template['placeholder_config'], str) else template['placeholder_config']
        
        if placeholder_config:
            teacher_data = get_teacher_data_by_config(teacher_id, placeholder_config)
        else:
            field_mappings = get_field_mappings()
            teacher_data = get_teacher_data(teacher_id, field_mappings)
        
        # 构建预览数据：有数据的显示数据，没数据的保留占位符
        preview_data = {}
        for ph in template_placeholders:
            if ph in teacher_data and teacher_data[ph]:
                preview_data[ph] = teacher_data[ph]
            else:
                # 没有数据时，保留占位符格式
                preview_data[ph] = '{{' + ph + '}}'
        
        # 生成填充后的临时文件
        template_path = template['file_path']
        temp_filename = f"preview_{template_id}_{teacher_id}.{file_ext}"
        output_path = os.path.join(tempfile.gettempdir(), temp_filename)
        
        # 生成填充后的文件
        if file_ext == 'docx':
            fill_docx_template(template_path, output_path, preview_data)
        else:
            fill_xlsx_template(template_path, output_path, preview_data)
        
        # 生成数据映射信息
        data_mapping = []
        for ph in template_placeholders:
            has_data = ph in teacher_data and teacher_data[ph]
            data_mapping.append({
                'placeholder': ph,
                'value': teacher_data.get(ph, ''),
                'has_data': has_data,
                'display': teacher_data.get(ph) if has_data else ('{{' + ph + '}}')
            })
        
        # 获取页面设置
        page_info = template.get('page_info')
        if page_info:
            page_info = json.loads(page_info) if isinstance(page_info, str) else page_info
        else:
            page_info = {
                "page_size": "A4",
                "orientation": "纵向",
                "page_width_mm": 210,
                "page_height_mm": 297
            }
        
        # 生成PDF预览（Word和Excel格式）
        pdf_url = ""
        pdf_filename = f"preview_{template_id}_{teacher_id}.pdf"
        pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)
        
        if file_ext == 'docx':
            if convert_docx_to_pdf(output_path, pdf_path):
                pdf_url = f"/api/universal-templates/download-preview/{pdf_filename}"
        elif file_ext in ['xlsx', 'xls']:
            # Excel：使用原始模板路径和预览数据直接转换PDF（保留格式）
            if convert_excel_to_pdf(template_path, pdf_path, preview_data):
                pdf_url = f"/api/universal-templates/download-preview/{pdf_filename}"
        
        return {
            "status": "success",
            "preview_url": f"/api/universal-templates/download-preview/{temp_filename}",
            "pdf_url": pdf_url,
            "data_mapping": data_mapping,
            "template_name": template['template_name'],
            "file_type": file_ext,
            "page_info": page_info
        }
        
    except Exception as e:
        print(f"预览失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")


@router.get("/download-preview/{filename}")
async def download_preview(filename: str, download: bool = Query(False, description="是否强制下载")):
    """下载预览文件"""
    try:
        file_path = os.path.join(tempfile.gettempdir(), filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="预览文件不存在")
        
        file_ext = filename.split('.')[-1]
        
        # 根据文件类型设置媒体类型
        if file_ext == 'docx':
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_ext == 'pdf':
            media_type = 'application/pdf'
        elif file_ext in ['xlsx', 'xls']:
            media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            media_type = 'application/octet-stream'
        
        # 设置响应头，inline表示在浏览器中预览，attachment表示下载
        # 使用 RFC 5987 编码处理中文文件名
        from urllib.parse import quote
        encoded_filename = quote(filename, safe='')
        headers = {}
        if download:
            headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        else:
            headers['Content-Disposition'] = f"inline; filename*=UTF-8''{encoded_filename}"
        
        return FileResponse(
            file_path,
            media_type=media_type,
            headers=headers
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"下载预览失败: {e}")
        raise HTTPException(status_code=500, detail=f"下载预览失败: {str(e)}")


def generate_preview_html(teacher_data: dict, template_name: str) -> str:
    """生成数据预览HTML"""
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="text-align: center; color: #333;">{template_name}</h2>
        <div style="max-width: 800px; margin: 0 auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
            <h3 style="border-bottom: 2px solid #409EFF; padding-bottom: 10px; color: #409EFF;">教师信息预览</h3>
            <table style="width: 100%; border-collapse: collapse;">
    """
    
    for key, value in teacher_data.items():
        display_value = value if value else '<span style="color: #999;">未填写</span>'
        html += f"""
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 12px; width: 30%; background: #f5f5f5; font-weight: bold; color: #333;">{key}</td>
                    <td style="padding: 12px; color: #666;">{display_value}</td>
                </tr>
        """
    
    html += """
            </table>
            <p style="color: #999; margin-top: 20px; text-align: center; font-size: 12px;">
                <i>注：此为数据预览，实际格式以导出文件为准</i>
            </p>
        </div>
    </div>
    """
    return html


# ============ 字段映射管理API ============

@router.get("/field-mappings")
async def get_field_mappings_api():
    """获取字段映射列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, placeholder, table_name, field_name, condition_field, is_active, created_at
            FROM universal_template_field_mapping
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": rows}
        
    except Exception as e:
        print(f"获取字段映射失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/field-mappings")
async def create_field_mapping(data: dict):
    """创建字段映射"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO universal_template_field_mapping (placeholder, table_name, field_name, condition_field)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (data.get('placeholder'), data.get('table_name'), data.get('field_name'), data.get('condition_field', 'teacher_id')))
        
        mapping_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "message": "映射创建成功", "data": {"id": mapping_id}}
        
    except Exception as e:
        print(f"创建字段映射失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/field-mappings/{mapping_id}")
async def delete_field_mapping(mapping_id: int):
    """删除字段映射"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM universal_template_field_mapping WHERE id = %s", (mapping_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "message": "映射已删除"}
        
    except Exception as e:
        print(f"删除字段映射失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
