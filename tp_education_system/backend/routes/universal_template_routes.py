"""
通用模板自动填报系统API路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
import shutil
import subprocess
import traceback
import asyncio
from datetime import datetime

from services.universal_template_service import template_engine, get_db_connection
from openpyxl import load_workbook

router = APIRouter(prefix="/api/universal-template", tags=["通用模板自动填报"])

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'templates')
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports', 'templates')
SAVED_DIR = os.path.join(EXPORT_DIR, '已保存')
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(SAVED_DIR, exist_ok=True)


def _init_saved_exports_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_exports (
                id SERIAL PRIMARY KEY,
                模板ID VARCHAR(100) NOT NULL,
                模板名称 VARCHAR(200),
                单位名称 VARCHAR(200),
                年月 VARCHAR(20),
                查询条件 JSONB DEFAULT '{}',
                统计范围 JSONB DEFAULT '{}',
                填报口径 JSONB DEFAULT '{}',
                Excel路径 VARCHAR(500),
                PDF路径 VARCHAR(500),
                保存时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                备注 TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("[OK] saved_exports表初始化成功")
    except Exception as e:
        print(f"[WARNING] saved_exports表初始化失败: {e}")

_init_saved_exports_table()

def _build_export_filename(config, request, include_seconds=False):
    now = datetime.now()
    next_month = now.month + 1
    next_year = now.year
    if next_month > 12:
        next_month = 1
        next_year += 1
    month_str = f"{next_year}年{next_month}月"
    date_str = now.strftime("%Y%m%d_%H%M%S") if include_seconds else now.strftime("%Y%m%d")
    unit_name = _get_fill_unit_name(request)
    name = config.get('模板名称', '')
    if unit_name:
        return f"{unit_name}{month_str}{name}({date_str})"
    return f"{month_str}{name}({date_str})"


def _get_fill_unit_name(request):
    if request.统计范围:
        scope = request.统计范围.get('单位范围', {})
        for level in ['学校', '镇', '县', '地区', '省']:
            if level in scope and scope[level].get('unit_name'):
                return scope[level]['unit_name']
    if request.查询条件:
        employee_id = request.查询条件.get('职工ID')
        if employee_id:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT uh.unit_name FROM teacher_basic_info t "
                    "JOIN teacher_unit tu ON t.id_card = tu.id_card "
                    "JOIN unit_hierarchy uh ON CAST(tu.unit_1 AS integer) = uh.id "
                    "WHERE t.id = %s",
                    (int(employee_id),)
                )
                row = cursor.fetchone()
                cursor.close()
                conn.close()
                if row:
                    return row[0]
            except Exception:
                pass
    return None


SOFFICE_PATHS = [
    shutil.which('soffice.exe'),
    shutil.which('soffice'),
    r'C:\Program Files\LibreOffice\program\soffice.exe',
    r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
]
SOFFICE_PATH = None
for p in SOFFICE_PATHS:
    if p and os.path.exists(p):
        SOFFICE_PATH = p
        break

LIBREOFFICE_PROFILE = os.path.join(EXPORT_DIR, '.libreoffice_profile')

if SOFFICE_PATH:
    print(f"[OK] LibreOffice检测成功: {SOFFICE_PATH}")
    os.makedirs(LIBREOFFICE_PROFILE, exist_ok=True)
    try:
        subprocess.run(
            [SOFFICE_PATH, '--headless',
             f'-env:UserInstallation=file:///{LIBREOFFICE_PROFILE.replace(os.sep, "/")}',
             '--terminate_after_init'],
            capture_output=True, text=True, timeout=30
        )
        print(f"[OK] LibreOffice配置文件初始化成功: {LIBREOFFICE_PROFILE}")
    except Exception as e:
        print(f"[WARNING] LibreOffice配置文件初始化失败: {e}")
else:
    print("[WARNING] 未检测到LibreOffice，PDF导出功能不可用")


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
    统计范围: Optional[Dict[str, Any]] = None
    填报口径: Optional[Dict[str, Any]] = None


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
    模板分类: str = Form(None),
    保存文件名: str = Form(None)
):
    try:
        save_filename = 保存文件名 if 保存文件名 else file.filename
        temp_path = os.path.join(TEMPLATE_DIR, save_filename)
        with open(temp_path, 'wb') as f:
            f.write(file.file.read())
        
        config = template_engine.import_template(temp_path, 模板名称, 模板类型)
        if 模板分类:
            config['模板分类'] = 模板分类
        
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
        统计范围: 五级单位层级
        填报口径: 选中的标签筛选条件
    
    返回:
        填充后的模板配置JSON
    """
    try:
        config = template_engine.load_template_config(request.模板ID)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        if request.统计范围:
            config['统计范围'] = request.统计范围
        if request.填报口径:
            config['填报口径'] = request.填报口径
        
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


def _find_latest_saved_file(template_id, unit_name, year_month):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT Excel路径, PDF路径 FROM saved_exports
               WHERE 模板ID = %s AND 单位名称 = %s AND 年月 = %s
               ORDER BY 保存时间 DESC LIMIT 1""",
            (template_id, unit_name, year_month)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row and row[0] and os.path.exists(row[0]):
            return {'Excel路径': row[0], 'PDF路径': row[1]}
        return None
    except Exception as e:
        print(f"[WARNING] 查找保存文件失败: {e}")
        return None


def _get_system_ym():
    now = datetime.now()
    m = now.month + 1
    y = now.year
    if m > 12:
        m = 1
        y += 1
    return f"{y}年{m}月"


def _do_full_fill_to_excel(config, request, output_path):
    if request.统计范围:
        config['统计范围'] = request.统计范围
    if request.填报口径:
        config['填报口径'] = request.填报口径
    mappings = template_engine.load_field_mappings(request.模板ID)
    config['字段映射'] = mappings
    filled_config = template_engine.fill_template_data(config, request.查询条件)
    original_path = config.get('原始文件路径')
    wb = load_workbook(original_path)
    ws = wb.active
    for cell_data in filled_config.get('单元格数据', []):
        row_num = cell_data.get('行号')
        col_num = cell_data.get('列号')
        display_val = cell_data.get('显示值', '')
        if row_num and col_num and display_val != '':
            try:
                s = str(display_val)
                if s.replace('-', '').replace('.', '').isdigit():
                    val = float(s) if '.' in s else int(s)
                else:
                    val = display_val
            except (ValueError, AttributeError):
                val = display_val
            ws.cell(row=row_num, column=col_num, value=val)
    wb.save(output_path)
    return output_path


@router.post("/export")
async def export_template(request: FillTemplateRequest):
    try:
        config = template_engine.load_template_config(request.模板ID)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")

        original_file_path = config.get('原始文件路径')
        if not original_file_path or not os.path.exists(original_file_path):
            raise HTTPException(status_code=404, detail="原始文件不存在")

        unit_name = _get_fill_unit_name(request)
        system_ym = _get_system_ym()
        saved = _find_latest_saved_file(request.模板ID, unit_name, system_ym)

        if saved:
            excel_path = saved['Excel路径']
            if os.path.exists(excel_path):
                return FileResponse(
                    excel_path,
                    filename=os.path.basename(excel_path),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        base_name = _build_export_filename(config, request)
        filename = f"{base_name}.xlsx"
        output_path = os.path.join(EXPORT_DIR, filename)

        _do_full_fill_to_excel(config, request, output_path)

        return FileResponse(
            output_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"导出失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
async def save_filled_template(request: FillTemplateRequest):
    try:
        config = template_engine.load_template_config(request.模板ID)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")

        original_file_path = config.get('原始文件路径')
        if not original_file_path or not os.path.exists(original_file_path):
            raise HTTPException(status_code=404, detail="原始文件不存在")

        base_name = _build_export_filename(config, request, include_seconds=True)
        xlsx_filename = f"{base_name}.xlsx"
        xlsx_path = os.path.join(SAVED_DIR, xlsx_filename)

        _do_full_fill_to_excel(config, request, xlsx_path)

        pdf_path = None
        if SOFFICE_PATH:
            try:
                xlsx_basename = os.path.basename(xlsx_path)
                result = await asyncio.to_thread(
                    lambda: subprocess.run(
                        [SOFFICE_PATH, '--headless',
                         f'-env:UserInstallation=file:///{LIBREOFFICE_PROFILE.replace(os.sep, "/")}',
                         '--convert-to', 'pdf', xlsx_filename, '--outdir', SAVED_DIR],
                        capture_output=True, text=True, timeout=120,
                        cwd=SAVED_DIR
                    )
                )
                if result.returncode == 0:
                    pdf_name = f"{base_name}.pdf"
                    candidate = os.path.join(SAVED_DIR, pdf_name)
                    if os.path.exists(candidate):
                        pdf_path = candidate
                else:
                    print(f"[WARNING] PDF转换失败: {result.stderr}")
            except Exception as e:
                print(f"[WARNING] PDF生成异常: {e}")

        now = datetime.now()
        unit_name = _get_fill_unit_name(request)
        system_ym = _get_system_ym()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO saved_exports (模板ID, 模板名称, 单位名称, 年月, 查询条件, 统计范围, 填报口径, Excel路径, PDF路径, 保存时间)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                request.模板ID,
                config.get('模板名称', ''),
                unit_name or '',
                system_ym,
                json.dumps(request.查询条件, ensure_ascii=False),
                json.dumps(request.统计范围, ensure_ascii=False) if request.统计范围 else '{}',
                json.dumps(request.填报口径, ensure_ascii=False) if request.填报口径 else '{}',
                xlsx_path,
                pdf_path or '',
                now
            )
        )
        conn.commit()
        cursor.close()
        conn.close()

        return {
            "成功": True,
            "消息": "保存成功",
            "数据": {
                "Excel文件": xlsx_filename,
                "PDF文件": os.path.basename(pdf_path) if pdf_path else None,
                "保存时间": now.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"保存失败: {e}")
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


@router.get("/download-template/{template_id}")
async def download_template(template_id: str):
    """
    下载原始模板文件（空表）

    参数:
        template_id: 模板ID
    返回:
        原始Excel文件下载
    """
    try:
        config = template_engine.load_template_config(template_id)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")

        original_file_path = config.get('原始文件路径', '')
        original_filename = config.get('原始文件', '')

        if not original_file_path or not os.path.exists(original_file_path):
            original_file_path = os.path.join(TEMPLATE_DIR, original_filename)

        if not os.path.exists(original_file_path):
            raise HTTPException(status_code=404, detail="原始模板文件不存在")

        download_filename = f"{config['模板名称']}_模板.xlsx"
        return FileResponse(
            original_file_path,
            filename=download_filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-libreoffice")
async def check_libreoffice():
    """检查服务器是否安装了LibreOffice"""
    return {
        "成功": True,
        "可用": SOFFICE_PATH is not None,
        "路径": SOFFICE_PATH or ""
    }


@router.post("/export-pdf")
async def export_pdf(request: FillTemplateRequest):
    if not SOFFICE_PATH:
        raise HTTPException(status_code=503, detail="服务器未安装LibreOffice，PDF导出不可用")

    try:
        config = template_engine.load_template_config(request.模板ID)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")

        original_file_path = config.get('原始文件路径')
        if not original_file_path or not os.path.exists(original_file_path):
            raise HTTPException(status_code=404, detail=f"原始文件不存在: {original_file_path}")

        unit_name = _get_fill_unit_name(request)
        system_ym = _get_system_ym()
        saved = _find_latest_saved_file(request.模板ID, unit_name, system_ym)

        if saved and saved.get('PDF路径') and os.path.exists(saved['PDF路径']):
            pdf_path = saved['PDF路径']
            return FileResponse(
                pdf_path,
                filename=os.path.basename(pdf_path),
                media_type="application/pdf"
            )

        base_name = _build_export_filename(config, request)
        xlsx_filename = f"{base_name}.xlsx"
        xlsx_path = os.path.join(EXPORT_DIR, xlsx_filename)

        _do_full_fill_to_excel(config, request, xlsx_path)

        if not os.path.exists(xlsx_path):
            raise Exception(f"XLSX文件未生成: {xlsx_path}")

        result = await asyncio.to_thread(
            lambda: subprocess.run(
                [SOFFICE_PATH, '--headless',
                 f'-env:UserInstallation=file:///{LIBREOFFICE_PROFILE.replace(os.sep, "/")}',
                 '--convert-to', 'pdf', xlsx_filename, '--outdir', EXPORT_DIR],
                capture_output=True, text=True, timeout=120,
                cwd=EXPORT_DIR
            )
        )

        if result.returncode != 0:
            raise Exception(f"LibreOffice转换失败: stdout={result.stdout} stderr={result.stderr}")

        pdf_path = os.path.join(EXPORT_DIR, f"{base_name}.pdf")
        if not os.path.exists(pdf_path):
            raise Exception(f"PDF文件未生成: {pdf_path}")

        pdf_filename = f"{base_name}.pdf"

        return FileResponse(
            pdf_path,
            filename=pdf_filename,
            media_type="application/pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"PDF导出失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-tables")
async def get_available_tables():
    """
    获取可用的数据表列表（用于字段映射配置的数据源表选择）
    从数据库中动态读取所有表，结合 table_name_mappings.json 提供中文表名
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="无法连接数据库")
        
        cur = conn.cursor()
        
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            AND table_name NOT LIKE '_prisma_%'
            AND table_name NOT LIKE 'pg_%'
            ORDER BY table_name
        """)
        db_tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        MAPPINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'table_name_mappings.json')
        chinese_map = {}
        if os.path.exists(MAPPINGS_FILE):
            with open(MAPPINGS_FILE, 'r', encoding='utf-8') as f:
                mappings_data = json.load(f)
            chinese_map = mappings_data.get('reverse_mappings', {})
        
        tables = []
        for eng_name in db_tables:
            chinese_name = chinese_map.get(eng_name, None)
            tables.append({
                '英文表名': eng_name,
                '中文表名': chinese_name,
                '显示名称': chinese_name if chinese_name else eng_name
            })
        
        return {'成功': True, '数据': tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _load_dict_relations_from_configs(table_name):
    """从 field_configs 目录加载 to_dict 关联关系，返回 [{中文字段名, targetField, 字典表, 字典值字段}]"""
    import os as _os
    try:
        configs_dir = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), 'config', 'field_configs')
        if not _os.path.exists(configs_dir):
            return []
        result = []
        for filename in _os.listdir(configs_dir):
            if not filename.endswith('.json'):
                continue
            filepath = _os.path.join(configs_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get('table_name') != table_name:
                    continue
                for fc in data.get('field_configs', []):
                    if fc.get('relation_type') == 'to_dict':
                        result.append({
                            '中文字段名': fc['sourceField'],
                            'targetField': fc.get('targetField', fc['sourceField']),
                            '字典表': fc.get('relation_table', ''),
                            '字典值字段': fc.get('relation_display_field', '')
                        })
            except Exception:
                pass
        return result
    except Exception:
        return []

def _query_dict_values(dict_table, value_field):
    """查询字典表的所有可选值"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cur = conn.cursor()
        cur.execute(f"SELECT DISTINCT \"{value_field}\" FROM \"{dict_table}\" WHERE \"{value_field}\" IS NOT NULL AND \"{value_field}\" != '' ORDER BY \"{value_field}\"")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]
    except Exception:
        return []

@router.get("/table-columns/{table_name}")
async def get_table_columns(table_name: str):
    """获取指定表的所有列信息（用于字段映射下拉选择）"""
    try:
        import psycopg2
        
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="无法连接数据库")
        
        cur = conn.cursor()
        
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = [{'字段名': row[0], '数据类型': row[1]} for row in cur.fetchall()]
        
        cur.execute("SELECT field_name, 关联类型, 关联表, 关联显示字段, 字段名 FROM table_field_relations WHERE table_name = %s", (table_name,))
        field_relations = {}
        for row in cur.fetchall():
            field_relations[row[0]] = {
                '关联类型': row[1], 
                '字典表': row[2], 
                '字典值字段': row[3],
                '中文字段名': row[4]
            }
        
        cur.close()
        conn.close()
        
        dict_relations_list = _load_dict_relations_from_configs(table_name)
        
        for col in columns:
            col_name = col['字段名']
            rel = field_relations.get(col_name, {})
            chinese_name = rel.get('中文字段名', col_name)
            
            rel2 = field_relations.get(chinese_name, {})
            if rel2 and rel2.get('中文字段名'):
                chinese_name = rel2.get('中文字段名', chinese_name)
            
            col['中文字段名'] = chinese_name
            col['显示名称'] = chinese_name
            
            matched_dict = None
            for dr in dict_relations_list:
                dr_chinese = dr['中文字段名']
                dr_target = dr['targetField']
                if chinese_name == dr_chinese or col_name == dr_chinese or chinese_name == dr_target or col_name == dr_target:
                    matched_dict = {'字典表': dr['字典表'], '字典值字段': dr['字典值字段']}
                    break
            if not matched_dict:
                for dr in dict_relations_list:
                    dr_value_field = dr['字典值字段']
                    if dr_value_field and (dr_value_field in col_name or col_name in dr_value_field):
                        matched_dict = {'字典表': dr['字典表'], '字典值字段': dr['字典值字段']}
                        break
            
            if matched_dict:
                col['关联字典'] = matched_dict
                col['字典可选值'] = _query_dict_values(matched_dict['字典表'], matched_dict['字典值字段'])
            elif rel.get('关联类型') == 'to_dict':
                col['关联字典'] = {'字典表': rel['字典表'], '字典值字段': rel['字典值字段']}
                col['字典可选值'] = _query_dict_values(rel['字典表'], rel['字典值字段'])
        
        return {'成功': True, '数据': columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dict-values/{table_name}")
async def get_dict_values(table_name: str):
    """
    获取字典表的所有可选值列表
    """
    try:
        DICT_CONFIGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'dict_tables_config.json')
        value_field = None
        label_field = None
        
        if os.path.exists(DICT_CONFIGS_FILE):
            with open(DICT_CONFIGS_FILE, 'r', encoding='utf-8') as f:
                dict_configs = json.load(f)
            for dt in dict_configs.get('dict_tables', []):
                if dt['table_name'] == table_name:
                    value_field = dt.get('value_field', '')
                    label_field = dt.get('label_field', '')
                    break
        
        if not value_field:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s ORDER BY ordinal_position LIMIT 1", (table_name,))
            first_col = cur.fetchone()
            cur.close()
            conn.close()
            value_field = first_col[0] if first_col else 'id'
            label_field = value_field
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT DISTINCT \"{label_field}\" FROM \"{table_name}\" WHERE \"{label_field}\" IS NOT NULL AND \"{label_field}\" != '' ORDER BY \"{label_field}\"")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        values = [{'值': row[0], '显示名称': str(row[0])} for row in rows]
        return {'成功': True, '数据': values, '字典表': table_name, '值字段': value_field}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags")
async def get_all_tags():
    """
    获取所有标签列表
    从 personal_dict_dictionary 表动态读取
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, biao_qian FROM personal_dict_dictionary ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        tags = [{'id': r[0], '标签名称': r[1]} for r in rows]

        return {
            '成功': True,
            '数据': tags
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-employee")
async def search_employee(
    keyword: str = Query(..., description="搜索关键词（身份证号/姓名/ID）")
):
    """
    根据身份证号、姓名或ID搜索职工
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if keyword.isdigit() and len(keyword) < 10:
            cur.execute(
                """SELECT id, name, id_card FROM teacher_basic_info WHERE id = %s LIMIT 5""",
                (int(keyword),)
            )
        else:
            cur.execute(
                """SELECT id, name, id_card FROM teacher_basic_info
                   WHERE name LIKE %s OR id_card LIKE %s LIMIT 10""",
                (f"%{keyword}%", f"%{keyword}%")
            )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        results = [{'职工ID': r[0], '姓名': r[1], '身份证号': r[2] or ''} for r in rows]

        return {'成功': True, '数据': results}
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


class HistoryQueryRequest(BaseModel):
    模板ID: str
    单位名称: Optional[str] = None
    起始日期: Optional[str] = None
    截止日期: Optional[str] = None


@router.post("/history")
async def query_history(request: HistoryQueryRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conditions = ["模板ID = %s"]
        params = [request.模板ID]
        if request.单位名称:
            conditions.append("单位名称 = %s")
            params.append(request.单位名称)
        if request.起始日期:
            conditions.append("保存时间 >= %s::date")
            params.append(request.起始日期)
        if request.截止日期:
            conditions.append("保存时间 <= %s::date + interval '1 day'")
            params.append(request.截止日期)
        where = " AND ".join(conditions)
        sql = f"SELECT id, 模板名称, 单位名称, 年月, 查询条件, Excel路径, PDF路径, 保存时间 FROM saved_exports WHERE {where} ORDER BY 保存时间 DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            entry = {
                "ID": row[0],
                "模板名称": row[1],
                "单位名称": row[2],
                "年月": row[3],
                "查询条件": row[4] if isinstance(row[4], dict) else json.loads(row[4]) if row[4] else {},
                "Excel路径": row[5],
                "PDF路径": row[6],
                "保存时间": row[7].strftime("%Y-%m-%d %H:%M:%S") if hasattr(row[7], 'strftime') else str(row[7])
            }
            results.append(entry)
        cursor.close()
        conn.close()
        return {"成功": True, "数据": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history-file/{record_id}")
async def download_history_file(record_id: int, format: str = "Excel"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Excel路径, PDF路径 FROM saved_exports WHERE id = %s", (record_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="记录不存在")
        excel_path, pdf_path = row[0], row[1]
        if format == "PDF" and pdf_path and os.path.exists(pdf_path):
            return FileResponse(
                pdf_path,
                filename=os.path.basename(pdf_path),
                media_type="application/pdf"
            )
        if excel_path and os.path.exists(excel_path):
            return FileResponse(
                excel_path,
                filename=os.path.basename(excel_path),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        raise HTTPException(status_code=404, detail="文件不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
