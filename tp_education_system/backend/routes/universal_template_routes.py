"""
通用模板自动填报系统API路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import json
import re
import copy
import shutil
import subprocess
import traceback
import asyncio
from datetime import datetime

from services.universal_template_service import template_engine, get_db_connection
from openpyxl import load_workbook
from openpyxl.styles import Alignment

router = APIRouter(prefix="/api/universal-template", tags=["通用模板自动填报"])

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
FIELD_CONFIGS_DIR = os.path.join(CONFIG_DIR, 'field_configs')
MAPPINGS_FILE = os.path.join(CONFIG_DIR, 'table_name_mappings.json')


def _load_table_mappings() -> Dict[str, str]:
    en_to_cn = {}
    if not os.path.exists(MAPPINGS_FILE):
        return en_to_cn
    with open(MAPPINGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for chinese_name, info in data.get('mappings', {}).items():
        english_name = info.get('english_name', '')
        if english_name:
            en_to_cn[english_name] = chinese_name
    return en_to_cn


def _load_field_configs_index() -> Dict[str, Dict[str, Any]]:
    index = {}
    if not os.path.exists(FIELD_CONFIGS_DIR):
        return index
    for filename in os.listdir(FIELD_CONFIGS_DIR):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(FIELD_CONFIGS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            table_name = data.get('table_name', '')
            if table_name:
                index[table_name] = {
                    'config_name': data.get('config_name', ''),
                    'table_type': data.get('table_type', 'master'),
                    'field_configs': data.get('field_configs', [])
                }
        except Exception:
            continue
    return index


def _resolve_chinese_datasource(datasource: str) -> str:
    if not datasource or datasource.startswith('公式:'):
        return datasource
    if '.' not in datasource:
        return datasource
    parts = datasource.split('.', 1)
    if len(parts) != 2:
        return datasource
    english_table, english_field = parts
    en_to_cn = _load_table_mappings()
    field_index = _load_field_configs_index()
    chinese_table = en_to_cn.get(english_table, english_table)
    config = field_index.get(english_table)
    chinese_field = english_field
    if config:
        for fc in config.get('field_configs', []):
            if fc.get('targetField', '') == english_field:
                chinese_field = fc.get('sourceField', english_field)
                break
    return f"{chinese_table}.{chinese_field}"

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
    # 优先使用用户选择的年月，没有则用当前系统年月
    user_ym = request.查询条件.get('年月', '') if request.查询条件 else ''
    if user_ym:
        ym_match = re.match(r'^(\d{4})-(\d{1,2})$', user_ym)
        if ym_match:
            year = int(ym_match.group(1))
            month = int(ym_match.group(2)) + 1
            if month > 12:
                month = 1
                year += 1
            month_str = f"{year}年{month}月"
        else:
            month_str = f"{now.year}年{now.month}月"
    else:
        month_str = f"{now.year}年{now.month}月"
    date_str = now.strftime("%Y%m%d_%H%M%S") if include_seconds else now.strftime("%Y%m%d")
    name = config.get('模板名称', '')
    unit_name = _get_fill_unit_name(request)
    template_category = config.get('模板分类', '')
    
    # 个人表：使用教师姓名
    if template_category == '个人表' and unit_name:
        return f"{unit_name}_{name}({date_str})"
    # 单位表：使用单位名称+年月
    if unit_name:
        return f"{unit_name}{month_str}{name}({date_str})"
    return f"{month_str}{name}({date_str})"


def _get_fill_unit_name(request):
    """获取导出文件名中的单位/个人名称
    
    对于个人表（查询条件包含身份证号或职工ID），返回教师姓名
    对于单位表，返回单位名称
    """
    if request.统计范围:
        scope = request.统计范围.get('单位范围', {})
        for level in ['学校', '镇', '县', '地区', '省']:
            if level in scope and scope[level].get('unit_name'):
                return scope[level]['unit_name']
    if request.查询条件:
        # 个人表：通过身份证号查询教师姓名
        id_card = request.查询条件.get('身份证号', '')
        if id_card:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM teacher_basic_info WHERE id_card = %s LIMIT 1",
                    (id_card.strip(),)
                )
                row = cursor.fetchone()
                cursor.close()
                conn.close()
                if row and row[0]:
                    return row[0]  # 返回教师姓名
            except Exception:
                pass
        
        # 个人表：通过职工ID查询教师姓名
        employee_id = request.查询条件.get('职工ID')
        if employee_id:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM teacher_basic_info WHERE id = %s",
                    (int(employee_id),)
                )
                row = cursor.fetchone()
                cursor.close()
                conn.close()
                if row and row[0]:
                    return row[0]  # 返回教师姓名
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
    字典值选择: Optional[List[Any]] = None


class FillTemplateRequest(BaseModel):
    模板ID: str
    查询条件: Dict[str, Any]
    统计范围: Optional[Dict[str, Any]] = None
    填报口径: Optional[Dict[str, Any]] = None
    备注: Optional[str] = None
    填报配置: Optional[Dict[str, Any]] = None  # 前端传来的已填充配置，用于保存时避免重新填充


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


class RemarksUpdateRequest(BaseModel):
    备注: Optional[str] = None
    模板名称: Optional[str] = None
    单位名称: Optional[str] = None
    年月: Optional[str] = None


@router.get("/remarks")
async def get_all_remarks():
    """获取所有已保存的导出记录（备注编辑用）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, 模板ID, 模板名称, 单位名称, 年月, 备注, 保存时间,
                   CASE WHEN Excel路径 IS NOT NULL AND Excel路径 != '' THEN true ELSE false END as 有Excel,
                   CASE WHEN PDF路径 IS NOT NULL AND PDF路径 != '' THEN true ELSE false END as 有PDF,
                   CASE WHEN "HTML路径" IS NOT NULL AND "HTML路径" != '' THEN true ELSE false END as 有HTML
            FROM saved_exports
            ORDER BY 保存时间 DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        records = []
        for row in rows:
            records.append({
                "ID": row[0],
                "模板ID": row[1],
                "模板名称": row[2],
                "单位名称": row[3] or '',
                "年月": row[4] or '',
                "备注": row[5] or '',
                "保存时间": row[6].strftime("%Y-%m-%d %H:%M:%S") if row[6] else '',
                "有Excel": row[7],
                "有PDF": row[8],
                "有HTML": row[9]
            })

        return {"成功": True, "数据": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remarks")
async def create_remarks(request: RemarksUpdateRequest):
    """手动创建一条备注记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute(
            """INSERT INTO saved_exports (模板ID, 模板名称, 单位名称, 年月, 查询条件, 统计范围, 填报口径, 备注, 保存时间)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                '',
                request.模板名称 or '',
                request.单位名称 or '',
                request.年月 or '',
                '{}',
                '{}',
                '{}',
                request.备注 or '',
                now
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"成功": True, "消息": "备注创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/remarks/{record_id}")
async def update_remarks(record_id: int, request: RemarksUpdateRequest):
    """更新导出记录的备注信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        updates = []
        values = []
        if request.备注 is not None:
            updates.append("备注 = %s")
            values.append(request.备注)
        if request.模板名称 is not None:
            updates.append("模板名称 = %s")
            values.append(request.模板名称)
        if request.单位名称 is not None:
            updates.append("单位名称 = %s")
            values.append(request.单位名称)
        if request.年月 is not None:
            updates.append("年月 = %s")
            values.append(request.年月)

        if not updates:
            cursor.close()
            conn.close()
            return {"成功": True, "消息": "无更新内容"}

        values.append(record_id)
        sql = f"UPDATE saved_exports SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        return {"成功": True, "消息": "更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/remarks/{record_id}")
async def delete_remarks(record_id: int):
    """删除导出记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saved_exports WHERE id = %s", (record_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return {"成功": True, "消息": "删除成功"}
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
async def preview_template(template_id: str, teacher_id: Optional[int] = None, id_card: Optional[str] = None, 年月: Optional[str] = None):
    """
    预览模板（返回完整元数据，用于Luckysheet渲染）
    
    参数:
        template_id: 模板ID
        teacher_id: 教师ID（可选，用于提取备注）
        id_card: 身份证号（可选，个人模板优先使用）
        年月: 用户选择的年月（如：2026-05），用于解析{{年月+1}}等日期占位符
    
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
        
        # 构建查询参数：优先使用id_card，其次使用teacher_id
        query_params = {}
        if 年月:
            query_params['年月'] = 年月
        if id_card:
            query_params['身份证号'] = id_card
        elif teacher_id is not None and teacher_id > 0:
            query_params['职工ID'] = str(teacher_id)
        
        # 如果有查询参数（身份证号或教师ID），先填充数据再渲染HTML
        filled_config = config
        备注 = ''
        if query_params and (id_card or (teacher_id is not None and teacher_id > 0)):
            try:
                # 加载字段映射
                mappings = template_engine.load_field_mappings(template_id)
                filled_config = copy.deepcopy(config)
                filled_config['字段映射'] = mappings
                filled_config = template_engine.fill_template_data(filled_config, query_params)
                
                # 提取备注信息
                if filled_config and '单元格数据' in filled_config:
                    for cell in filled_config['单元格数据']:
                        显示值 = str(cell.get('显示值', '') or '')
                        if 显示值.startswith('备注：'):
                            备注 = 显示值.replace('备注：', '').strip()
                            break
            except Exception as e:
                print(f"填充数据失败: {e}")
                import traceback
                traceback.print_exc()
        
        return {
            "成功": True,
            "数据": {
                "metadata": metadata,
                "HTML": template_engine.preview_template(filled_config, query_params, excel_path=original_file_path),
                "模板名称": config['模板名称'],
                "模板ID": template_id,
                "备注": 备注
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"预览错误: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/find-teacher-by-idcard")
async def find_teacher_by_idcard(id_card: str = Query(..., description="身份证号码")):
    """
    根据身份证号查找教师信息
    
    参数:
        id_card: 身份证号码（18位）
    
    返回:
        教师基本信息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, name, id_card FROM teacher_basic_info WHERE id_card = %s LIMIT 1",
                (id_card.strip(),)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "成功": True,
                    "数据": {
                        "id": row[0],
                        "姓名": row[1],
                        "身份证号": row[2]
                    }
                }
            else:
                return {
                    "成功": False,
                    "消息": "未找到该身份证号对应的教师"
                }
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
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
            request.转换函数,
            request.默认值,
            request.字典值选择
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
        字段映射字典（包含数据源_中文字段，直接从表名映射和字段配置文件解析）
    """
    try:
        mappings = template_engine.load_field_mappings(template_id)
        for field_name, mapping in mappings.items():
            datasource = mapping.get('数据源', '')
            if datasource:
                mapping['数据源_中文'] = _resolve_chinese_datasource(datasource)
        return {
            "成功": True,
            "数据": mappings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/field-mapping/{template_id}/{field_name}")
async def delete_field_mapping(template_id: str, field_name: str):
    try:
        deleted = template_engine.delete_field_mapping(template_id, field_name)
        if deleted:
            return {"成功": True, "消息": "字段映射已删除"}
        else:
            return {"成功": False, "消息": "未找到该字段映射"}
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
        # #region debug-point A:fill-entry
        import json as _dj, time as _dt
        _logp = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_fill_log.txt')
        with open(_logp, 'a', encoding='utf-8') as _df:
            _df.write(f"[{_dt.time()}] A:fill_entry 模板ID={request.模板ID} 查询条件={request.查询条件} 统计范围={request.统计范围} 填报口径={request.填报口径}\n")
        # #endregion
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
        
        html = template_engine.generate_print_html(filled_config, request.查询条件, excel_path=config.get('原始文件路径'))
        
        # 提取备注信息（从填充后的单元格数据中）
        备注 = ''
        if filled_config and '单元格数据' in filled_config:
            for cell in filled_config['单元格数据']:
                显示值 = str(cell.get('显示值', '') or '')
                if 显示值.startswith('备注：'):
                    备注 = 显示值.replace('备注：', '').strip()
                    break
        
        return {
            "成功": True,
            "数据": {
                "配置": filled_config,
                "HTML": html,
                "备注": 备注
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"填报失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-remarks")
def get_performance_remarks(year: int = datetime.now().year, month: int = datetime.now().month):
    """
    获取绩效工资审批表的备注信息
    
    参数:
        year: 年份
        month: 月份
    
    返回:
        格式化的备注信息
    """
    try:
        remarks = template_engine.get_performance_remarks(year, month)
        return {"成功": True, "数据": {"备注": remarks}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _find_latest_saved_file(template_id, unit_name, year_month):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT Excel路径, PDF路径, "HTML路径" FROM saved_exports
               WHERE 模板ID = %s AND 单位名称 = %s AND 年月 = %s
               ORDER BY 保存时间 DESC LIMIT 1""",
            (template_id, unit_name, year_month)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row and row[0] and os.path.exists(row[0]):
            return {'Excel路径': row[0], 'PDF路径': row[1], 'HTML路径': row[2]}
        return None
    except Exception as e:
        print(f"[WARNING] 查找保存文件失败: {e}")
        return None


def _get_system_ym():
    now = datetime.now()
    return f"{now.year}年{now.month}月"


def _write_filled_to_excel(config, filled_config, output_path):
    original_path = config.get('原始文件路径')
    wb = load_workbook(original_path)
    ws = wb.active

    max_line_count = {}  # 记录每行最大行数

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
            cell = ws.cell(row=row_num, column=col_num, value=val)
            if isinstance(val, str) and ('\n' in val or '\r' in val):
                cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                line_count = val.count('\n') + 1
                if row_num not in max_line_count or line_count > max_line_count[row_num]:
                    max_line_count[row_num] = line_count

    for merge_cell in filled_config.get('合并单元格', []):
        start = merge_cell.get('起始', '')
        end = merge_cell.get('结束', '')
        if start and end:
            ws.merge_cells(f'{start}:{end}')

    for row_num, line_count in max_line_count.items():
        line_height = 16
        ws.row_dimensions[row_num].height = max(line_count * line_height, 30)

    for merge_cell in filled_config.get('合并单元格', []):
        start = merge_cell.get('起始', '')
        if start:
            try:
                col_letter, row_num = start[0], int(start[1:])
                cell = ws.cell(row=row_num, column=ord(col_letter) - ord('A') + 1)
                if cell.value and isinstance(cell.value, str) and ('\n' in cell.value or '\r' in cell.value):
                    cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
            except Exception:
                pass

    wb.save(output_path)
    return output_path


def _do_full_fill_to_excel(config, request, output_path):
    if request.统计范围:
        config['统计范围'] = request.统计范围
    if request.填报口径:
        config['填报口径'] = request.填报口径
    mappings = template_engine.load_field_mappings(request.模板ID)
    config['字段映射'] = mappings
    filled_config = template_engine.fill_template_data(config, request.查询条件)
    _write_filled_to_excel(config, filled_config, output_path)
    return filled_config


@router.post("/export")
async def export_template(request: FillTemplateRequest):
    try:
        config = template_engine.load_template_config(request.模板ID)
        if not config:
            raise HTTPException(status_code=404, detail="模板不存在")

        original_file_path = config.get('原始文件路径')
        if not original_file_path or not os.path.exists(original_file_path):
            raise HTTPException(status_code=404, detail="原始文件不存在")

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

        # 使用前端传来的已填充配置（避免重复填充，保证数据一致性）
        if request.填报配置:
            filled_config = request.填报配置
            # 如果有编辑后的备注，也要更新到填报配置中（双保险）
            if request.备注:
                for cell in filled_config.get('单元格数据', []):
                    显示值 = str(cell.get('显示值', '') or '')
                    if 显示值.startswith('备注：') or 显示值 == '备注' or '备注' in 显示值:
                        cell['显示值'] = f"备注：\n{request.备注}"
                        cell['值'] = cell['显示值']
                        break
            _write_filled_to_excel(config, filled_config, xlsx_path)
        else:
            # 兜底：没有填报配置时，重新填充
            filled_config = _do_full_fill_to_excel(config, request, xlsx_path)
            if request.备注:
                for cell in filled_config.get('单元格数据', []):
                    显示值 = str(cell.get('显示值', '') or '')
                    if 显示值.startswith('备注：') or 显示值 == '备注' or '备注' in 显示值:
                        cell['显示值'] = request.备注 if not 显示值.startswith('备注：') else f"备注：{request.备注}"
                        _write_filled_to_excel(config, filled_config, xlsx_path)
                        break
                else:
                    _write_filled_to_excel(config, filled_config, xlsx_path)

        filled_html = template_engine.generate_print_html(filled_config, request.查询条件, excel_path=config.get('原始文件路径'))
        html_path = None
        if filled_html:
            html_name = f"{base_name}.html"
            html_path = os.path.join(SAVED_DIR, html_name)
            with open(html_path, 'w', encoding='utf-8') as fh:
                fh.write(filled_html)

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
                print(f"[WARNING] 文件转换异常: {e}")

        now = datetime.now()
        unit_name = _get_fill_unit_name(request)
        # 使用用户选择的年月，月份+1（报表月份 = 填报月份 + 1）
        user_ym = request.查询条件.get('年月', '') if request.查询条件 else ''
        if user_ym:
            ym_match = re.match(r'^(\d{4})-(\d{1,2})$', user_ym)
            if ym_match:
                year = int(ym_match.group(1))
                month = int(ym_match.group(2)) + 1
                if month > 12:
                    month = 1
                    year += 1
                user_ym = f"{year}年{month}月"
        system_ym = user_ym if user_ym else _get_system_ym()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO saved_exports (模板ID, 模板名称, 单位名称, 年月, 查询条件, 统计范围, 填报口径, Excel路径, PDF路径, "HTML路径", 保存时间)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
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
                html_path or '',
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
                "HTML文件": os.path.basename(html_path) if html_path else None,
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
            AND table_type IN ('BASE TABLE', 'VIEW')
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


# 全局缓存和翻译器
_field_configs_cache = {}
_en_to_cn_global = {}
_cn_to_en = {}

def _build_global_en_to_cn_map():
    global _en_to_cn_global, _cn_to_en
    if _en_to_cn_global:
        return
    import os as _os
    configs_dir = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), 'config', 'field_configs')
    if not _os.path.exists(configs_dir):
        return
    for filename in _os.listdir(configs_dir):
        if not filename.endswith('.json'):
            continue
        filepath = _os.path.join(configs_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for fc in data.get('field_configs', []):
                sf = fc.get('sourceField', '')
                tf = fc.get('targetField', sf)
                rdf = fc.get('relation_display_field', '')
                rt = fc.get('relation_type', '')
                if tf and tf != sf and all(c.isascii() and (c.isalnum() or c == '_') for c in tf):
                    if tf not in _en_to_cn_global:
                        _en_to_cn_global[tf] = sf
                        _cn_to_en[sf] = tf
                if rt in ('to_master', 'to_dict') and rdf and rdf != sf and all(c.isascii() and (c.isalnum() or c == '_') for c in rdf):
                    if rdf not in _en_to_cn_global:
                        _en_to_cn_global[rdf] = sf
        except Exception:
            pass

_COLUMN_WORD_MAP = {
    'id': 'ID', 'name': '名称', 'code': '编码', 'type': '类型', 'date': '日期',
    'time': '时间', 'year': '年份', 'month': '月份', 'status': '状态',
    'title': '标题', 'description': '描述', 'remark': '备注', 'remarks': '备注',
    'amount': '金额', 'count': '数量', 'people': '人数', 'person': '人',
    'standard': '标准', 'total': '合计', 'subtotal': '小计',
    'unit': '单位', 'level': '级别', 'category': '类别', 'tag': '标签',
    'school': '学校', 'teacher': '教师', 'student': '学生', 'employee': '职工',
    'phone': '电话', 'address': '地址', 'email': '邮箱', 'gender': '性别',
    'birth': '出生', 'age': '年龄', 'work': '工作', 'start': '开始', 'end': '结束',
    'entry': '进入', 'retire': '退休', 'retired': '退休', 'death': '死亡',
    'salary': '工资', 'pay': '工资', 'wage': '工资', 'subsidy': '补贴',
    'performance': '绩效', 'approval': '审批', 'report': '报表', 'export': '导出',
    'template': '模板', 'config': '配置', 'setting': '设置', 'rule': '规则',
    'detail': '明细', 'record': '记录', 'log': '日志', 'history': '历史',
    'backup': '备份', 'data': '数据', 'info': '信息', 'file': '文件',
    'path': '路径', 'source': '来源', 'target': '目标', 'note': '说明',
    'notes': '说明', 'content': '内容', 'value': '值', 'key': '键',
    'order': '顺序', 'sort': '排序', 'active': '激活', 'enabled': '启用',
    'effective': '生效', 'expiry': '到期', 'cancel': '取消', 'change': '变动',
    'registration': '登记', 'certificate': '证书', 'cert': '证书',
    'major': '专业', 'degree': '学位', 'education': '教育', 'training': '培训',
    'professional': '专业', 'technical': '技术', 'position': '岗位', 'post': '岗位',
    'job': '职务', 'duty': '职务', 'appointment': '聘任', 'hire': '雇用',
    'native': '籍贯', 'place': '地点', 'household': '户籍', 'ethnicity': '民族',
    'cadre': '干部', 'worker': '工人', 'official': '干部',
    'current': '当前', 'new': '新', 'old': '旧', 'original': '原始',
    'monthly': '月度', 'yearly': '年度', 'daily': '每日',
    'created': '创建', 'updated': '更新', 'creator': '创建人', 'updater': '更新人',
    'handler': '处理人', 'assignee': '负责人', 'operator': '操作人',
    'parent': '父级', 'child': '子级', 'root': '根',
    'prefix': '前缀', 'suffix': '后缀', 'display': '显示', 'hidden': '隐藏',
    'required': '必填', 'optional': '可选', 'default': '默认',
    'format': '格式', 'length': '长度', 'width': '宽度', 'height': '高度',
    'page': '页面', 'margin': '边距', 'orientation': '方向', 'landscape': '横向',
    'portrait': '纵向', 'paper': '纸张', 'size': '尺寸',
    'header': '表头', 'footer': '表尾', 'body': '正文', 'row': '行', 'col': '列',
    'merge': '合并', 'cell': '单元格', 'region': '区域',
    'x0': '左', 'y0': '上', 'x1': '右', 'y1': '下',
    'legacy': '遗留', 'issue': '问题', 'issues': '问题',
    'town': '乡镇', 'village': '村', 'city': '城市', 'province': '省份',
    'nation': '国家', 'country': '国家',
    'bank': '银行', 'account': '账户', 'card': '卡',
    'contact': '联系', 'relation': '关系', 'family': '家庭', 'member': '成员',
    'party': '党派', 'join': '加入', 'only': '独生', 'child_only': '独生子女',
    'pension': '退休金', 'insurance': '保险',
    'census': '户籍', 'residence': '居住', 'current_residence': '现居住地',
    'todo': '待办', 'task': '任务', 'trigger': '触发', 'condition': '条件',
    'message': '消息', 'notification': '通知',
    'filled': '已填报', 'saved': '已保存', 'exported': '已导出',
    'uploaded': '已上传', 'downloaded': '已下载', 'scanned': '已扫描',
    'generate': '生成', 'generated': '已生成', 'generation': '生成',
    'fill': '填报', 'filling': '填报',
    'step': '步骤', 'flow': '流程', 'process': '过程', 'progress': '进度',
    'completed': '已完成', 'returned': '已退回', 'return': '退回',
    'archive': '档案', 'archived': '已归档',
    'admin': '管理', 'manage': '管理', 'management': '管理',
    'system': '系统', 'user': '用户', 'role': '角色', 'permission': '权限',
    'password': '密码', 'token': '令牌', 'session': '会话',
    'api': '接口', 'endpoint': '端点', 'request': '请求', 'response': '响应',
    'error': '错误', 'warning': '警告', 'success': '成功', 'failed': '失败',
    'pending': '待处理', 'processing': '处理中', 'reviewing': '审核中',
    'approved': '已批准', 'rejected': '已拒绝',
    'pdf': 'PDF', 'excel': 'Excel', 'word': 'Word', 'xml': 'XML',
    'json': 'JSON', 'html': 'HTML', 'csv': 'CSV', 'image': '图片',
    'text': '文本', 'number': '数字', 'string': '字符串', 'boolean': '布尔',
    'integer': '整数', 'float': '浮点', 'decimal': '小数',
    'select': '选择', 'input': '输入', 'output': '输出', 'search': '搜索',
    'filter': '过滤', 'query': '查询', 'sort_by': '排序依据',
    'group': '分组', 'aggregate': '聚合', 'sum': '求和', 'avg': '平均',
    'max': '最大', 'min': '最小', 'count': '计数', 'product': '乘积',
    'calculation': '计算', 'calculate': '计算', 'formula': '公式',
    'field': '字段', 'table': '表', 'column': '列', 'row_num': '行号',
    'col_num': '列号', 'cell_num': '单元格号',
    'mapping': '映射', 'relation': '关系', 'reference': '引用',
    'foreign': '外键', 'primary': '主键', 'unique_key': '唯一键',
    'index': '索引', 'constraint': '约束', 'schema': '模式',
    'auto': '自动', 'manual': '手动', 'batch': '批量', 'single': '单个',
    'multi': '多个', 'all': '全部', 'none': '无', 'any': '任意',
    'every': '每个', 'each': '每', 'per': '每',
    'before': '之前', 'after': '之后', 'during': '期间',
    'from': '从', 'to': '到', 'by': '由', 'via': '通过',
    'online': '在线', 'offline': '离线', 'local': '本地', 'remote': '远程',
    'internal': '内部', 'external': '外部', 'public': '公开', 'private': '私有',
    'result': '结果', 'summary': '汇总', 'statistics': '统计', 'stats': '统计',
    'total_people': '总人数', 'total_amount': '总金额',
    'people_count': '人数', 'subsidy_amount': '补贴金额',
    'subsidy_standard': '补贴标准', 'subsidy_people': '补贴人数',
    'report_unit': '填报单位', 'report_date': '填报日期', 'report_period': '填报期间',
    'level_name': '级别名称', 'level_code': '级别编码',
    'monthly_standard': '月度标准', 'effective_date': '生效日期',
    'retired_cadre_count': '退休干部人数', 'retired_worker_count': '退休工人人数',
    'legacy_total_amount': '遗留总金额', 'legacy_total_people': '遗留总人数',
    'no_subsidy_count': '无补贴人数', 'excel_file_path': 'Excel文件路径',
    'pdf_file_path': 'PDF文件路径', 'scanned_file_path': '扫描文件路径',
    'teacher_id': '教师ID', 'teacher_name': '教师姓名',
    'id_card': '身份证号码', 'id_card_1': '身份证号码1', 'id_card_2': '身份证号码2',
    'birth_date': '出生日期', 'archive_birth_date': '档案出生日期',
    'work_start_date': '参加工作日期', 'retirement_date': '退休日期',
    'contact_phone': '联系电话', 'contact_phone_1': '联系电话1',
    'contact_phone_2': '联系电话2',
    'created_at': '创建时间', 'updated_at': '更新时间',
    'created_by': '创建人', 'updated_by': '更新人',
    'is_active': '是否启用', 'is_enabled': '是否启用',
    'is_cadre': '是否干部', 'is_only_child': '是否独生子女',
    'is_landscape': '是否横向', 'is_required': '是否必填',
    'is_visible': '是否可见',
    'is_read': '是否已读', 'is_admin': '是否管理员',
    'employment_status': '任职状态', 'work_years': '工作年限',
    'job_title': '职务', 'job_title_post': '职务岗位',
    'post_level': '岗位等级', 'post_level_1': '岗位等级1',
    'post_time': '岗位时间',
    'professional_title': '职称', 'professional_title_1': '职称1',
    'professional_title_2': '职称2', 'professional_title_3': '职称3',
    'professional_title_time': '职称取得时间',
    'graduation_school': '毕业学校', 'graduation_date': '毕业日期',
    'entry_date': '进入本单位日期', 'pension_unit': '退休金单位',
    'retirement_reason': '退休原因', 'retirement_address': '退休后居住地址',
    'retirement_certificate_number': '退休证编号',
    'birth_date_display': '出生日期显示', 'work_start_date_display': '参加工作日期显示',
    'work_years_display': '工作年限显示',
    'receive_date': '签收日期', 'recipient_name': '签收人',
    'sort_order': '排序号', 'task_items': '任务项',
    'due_date': '到期日期', 'plan_date': '计划日期',
    'remind_days': '提醒天数', 'advance_notice': '提前通知',
    'completed_at': '完成时间', 'started_at': '开始时间',
    'returned_at': '退回时间', 'return_reason': '退回原因',
    'return_count': '退回次数',
    'handle_time': '处理时间', 'handle_note': '处理备注',
    'trigger_time': '触发时间', 'trigger_reason': '触发原因',
    'trigger_type': '触发类型', 'trigger_value': '触发值',
    'listen_table': '监听表', 'listen_field': '监听字段',
    'old_value': '旧值', 'new_value': '新值',
    'template_id': '模板ID', 'template_code': '模板编码',
    'template_name': '模板名称', 'template_type': '模板类型',
    'file_name': '文件名', 'file_path': '文件路径', 'file_size': '文件大小',
    'file_type': '文件类型', 'file_format': '文件格式',
    'business_type': '业务类型', 'business_id': '业务ID',
    'related_type': '关联类型', 'related_id': '关联ID',
    'action': '操作', 'action_taken': '已执行操作',
    'fill_type': '填报类型', 'fill_target': '填报目标',
    'fill_date': '填报日期', 'filled_by': '填报人',
    'original_filename': '原始文件名', 'original_file_path': '原始文件路径',
    'original_status': '原始状态', 'new_status': '新状态',
    'original_post': '原始岗位', 'new_post': '新岗位',
    'original_retirement_date': '原始退休日期', 'new_retirement_date': '新退休日期',
    'delay_months': '延迟月数', 'estimate_type': '估算类型',
    'change_type': '变动类型', 'change_date': '变动日期',
    'change_content': '变动内容', 'change_reason': '变动原因',
    'change_category': '变动类别', 'change_detail': '变动详情',
    'effective_month': '生效月份', 'expiry_month': '到期月份',
    'cancel_performance_month': '取消绩效月份',
    'generation_params': '生成参数', 'generated_file_path': '生成文件路径',
    'generated_file_name': '生成文件名', 'generated_at': '生成时间',
    'generated_by': '生成人', 'error_message': '错误信息',
    'template_file_path': '模板文件路径',
    'source_type': '来源类型', 'source_config': '来源配置',
    'intermediate_table': '中间表', 'intermediate_table_cn': '中间表中文名',
    'intermediate_field': '中间字段', 'intermediate_field_cn': '中间字段中文名',
    'placeholder_name': '占位符名', 'placeholder_config': '占位符配置',
    'placeholder': '占位符', 'placeholders': '占位符',
    'activation_type': '激活类型', 'activation_config': '激活配置',
    'label_pattern': '标签模式', 'date_format': '日期格式',
    'format_type': '格式类型', 'table_index': '表序号',
    'row_index': '行序号', 'cell_index': '单元格序号',
    'page_num': '页码', 'x_pos': 'X位置', 'y_pos': 'Y位置',
    'css_selector': 'CSS选择器', 'page_width': '页面宽度',
    'page_height': '页面高度', 'paper_size': '纸张尺寸',
    'margin_top': '上边距', 'margin_bottom': '下边距',
    'margin_left': '左边距', 'margin_right': '右边距',
    'width_cm': '宽度厘米', 'height_cm': '高度厘米',
    'margin_left_cm': '左边距厘米', 'margin_right_cm': '右边距厘米',
    'margin_top_cm': '上边距厘米', 'margin_bottom_cm': '下边距厘米',
    'full_path': '完整路径', 'parent_id': '父级ID',
    'school_dict_id': '学校字典ID', 'unit_hierarchy': '单位层级',
    'unit_level': '单位级别', 'unit_name': '单位名称',
    'module_id': '模块ID', 'modules_data': '模块数据',
    'backup_name': '备份名称',
    'record_id': '记录ID', 'field_id': '字段ID', 'field_name': '字段名',
    'field_label': '字段标签', 'field_type': '字段类型',
    'field_value': '字段值', 'value_type': '值类型',
    'calculation_formula': '计算公式', 'depends_on_fields': '依赖字段',
    'logic_type': '逻辑类型', 'logic_operator': '逻辑运算符',
    'aggregate_func': '聚合函数', 'filter_condition': '过滤条件',
    'tag_name': '标签名', 'tag_name_cn': '标签中文名',
    'tag_id': '标签ID', 'tag_color': '标签颜色',
    'condition_name': '条件名称', 'condition_id': '条件ID',
    'user_id': '用户ID', 'user_name': '用户名',
    'assignee_id': '负责人ID', 'assignee_name': '负责人姓名',
    'related_teacher_id': '关联教师ID', 'related_teacher_name': '关联教师姓名',
    'log_id': '日志ID', 'usage_count': '使用次数',
    'last_used_at': '最后使用时间',
    'row_count': '行数', 'col_count': '列数',
    'cell_count': '单元格数', 'merge_count': '合并单元格数',
    'metadata_path': '元数据路径',
    'config_json': '配置JSON', 'data_json': '数据JSON',
    'progress_update_time': '进度更新时间', 'start_process_time': '开始处理时间',
    'complete_time': '完成时间', 'create_time': '创建时间',
}

def _generate_chinese_column_name(col_name):
    _build_global_en_to_cn_map()
    
    if col_name in _COLUMN_WORD_MAP:
        return _COLUMN_WORD_MAP[col_name]
    
    if col_name in _en_to_cn_global:
        return _en_to_cn_global[col_name]
    
    parts = col_name.split('_')
    if len(parts) == 1:
        return col_name
    
    translated = []
    for part in parts:
        if part in _COLUMN_WORD_MAP:
            translated.append(_COLUMN_WORD_MAP[part])
        else:
            translated.append(part)
    
    if translated[0] == 'is' and len(translated) >= 2:
        rest = ''.join(translated[1:])
        return '是否' + rest
    
    result = ''.join(translated)
    
    if result == col_name:
        return col_name
    
    return result

def _resolve_chinese_name(col_name, field_relations, en_to_cn, source_fields, biz_col_names, field_name_map=None):
    rel = field_relations.get(col_name, {})
    chinese_name = rel.get('中文字段名', '')
    
    if not chinese_name:
        chinese_name = en_to_cn.get(col_name, '')
    
    if not chinese_name and field_name_map:
        chinese_name = field_name_map.get(col_name.lower(), '')
    
    if not chinese_name:
        try:
            idx = biz_col_names.index(col_name) if col_name in biz_col_names else -1
            if 0 <= idx < len(source_fields):
                chinese_name = source_fields[idx]
        except ValueError:
            pass
    
    if not chinese_name:
        chinese_name = _generate_chinese_column_name(col_name)
    
    return chinese_name

def _load_dict_relations_from_configs(table_name):
    """从 field_configs 目录加载: dict_relations(字典关联), source_fields(中文字段名顺序列表), en_to_cn(英文→中文映射), field_name_map(英文字段名→中文字段名映射)"""
    import os as _os
    configs_dir = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), 'config', 'field_configs')
    if not _os.path.exists(configs_dir):
        return [], [], {}, {}
    
    dict_relations = []
    source_fields = []
    en_to_cn = {}
    field_name_map = {}
    
    for filename in _os.listdir(configs_dir):
        if not filename.endswith('.json'):
            continue
        filepath = _os.path.join(configs_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            t_name = data.get('table_name', '')
            
            for fc in data.get('field_configs', []):
                sf = fc.get('sourceField', '')
                tf = fc.get('targetField', sf)
                rdf = fc.get('relation_display_field', '')
                rt = fc.get('relation_type', '')
                
                if t_name == table_name:
                    if tf.lower() not in field_name_map:
                        field_name_map[tf.lower()] = sf
                    if rt == 'to_dict':
                        dict_relations.append({
                            '中文字段名': sf,
                            'targetField': tf,
                            '字典表': fc.get('relation_table', ''),
                            '字典值字段': rdf
                        })
                    source_fields.append(sf)
                
                if rt == 'to_master' and sf and rdf and sf != rdf:
                    if rdf not in en_to_cn:
                        en_to_cn[rdf] = sf
                elif rt == 'to_dict' and sf and rdf and sf != rdf:
                    if rdf not in en_to_cn:
                        en_to_cn[rdf] = sf
                    
        except Exception:
            pass
    
    return dict_relations, source_fields, en_to_cn, field_name_map

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
        
        dict_relations_list, source_fields, en_to_cn, field_name_map = _load_dict_relations_from_configs(table_name)
        
        skip_cols = {'id', 'created_at', 'updated_at'}
        biz_col_names = [c['字段名'] for c in columns if c['字段名'] not in skip_cols]
        
        for col in columns:
            col_name = col['字段名']
            
            chinese_name = _resolve_chinese_name(col_name, field_relations, en_to_cn, source_fields, biz_col_names, field_name_map)
            
            col['中文字段名'] = chinese_name
            col['显示名称'] = chinese_name
        
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


@router.get("/table-distinct-values/{table_name}/{column_name}")
async def get_table_distinct_values(table_name: str, column_name: str):
    """查询指定表指定字段的可选值列表（用于前端下拉筛选）。
    
    原则：数据源表决定数据源字段，数据源字段决定可选值来源。
    
    - 如果字段有关联字典表 → 从字典表查询全部值（全集），保证通用性。
      字典表是标准全集，不同单位可能只用到其中一部分。
      如果只取当前表的子集，未来新出现的值将无法被筛选，导致数据失真。
    - 如果字段无字典关联 → 从当前表查 distinct 值（保持原有逻辑）。
    """
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="无法连接数据库")
        cur = conn.cursor()

        dict_table = None
        dict_id_field = 'id'
        dict_label_field = None

        cur.execute("""
            SELECT "关联表", "关联字段", "关联显示字段"
            FROM table_field_relations
            WHERE "表名" = %s AND "字段名" = %s AND "关联类型" = 'dict' AND "关联表" IS NOT NULL
            LIMIT 1
        """, (table_name, column_name))
        rel = cur.fetchone()

        if rel:
            dict_table = rel[0]
            dict_id_field = rel[1] or 'id'
            dict_label_field = rel[2]
        else:
            dict_relations_list, _, _, _ = _load_dict_relations_from_configs(table_name)
            for dr in dict_relations_list:
                tf = dr.get('targetField', '')
                if tf.lower() == column_name.lower():
                    dict_table = dr.get('字典表', '')
                    dict_label_field = dr.get('字典值字段', '')
                    dict_id_field = 'id'
                    break

        if dict_table and dict_label_field:
            if not dict_label_field:
                cur.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position LIMIT 1
                """, (dict_table,))
                lc = cur.fetchone()
                dict_label_field = lc[0] if lc else 'id'

            try:
                query = f'SELECT "{dict_id_field}", "{dict_label_field}" FROM "{dict_table}" ORDER BY "{dict_id_field}"'
                cur.execute(query)
                rows = cur.fetchall()
                resolved = [{'值': row[0], '标签': str(row[1]) if row[1] is not None else str(row[0])} for row in rows]
                cur.close()
                conn.close()
                return {'成功': True, '数据': resolved, '表名': table_name, '字段名': column_name, '数量': len(resolved), '已解析': True}
            except Exception:
                pass

        cur.execute("""
            SELECT data_type FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """, (table_name, column_name))
        col_info = cur.fetchone()
        data_type = (col_info[0] or '').lower() if col_info else ''

        numeric_types = {'integer', 'bigint', 'smallint', 'numeric', 'decimal', 'real', 'double precision', 'serial', 'bigserial', 'smallserial'}
        is_numeric = data_type in numeric_types

        if is_numeric:
            query = f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL ORDER BY "{column_name}"'
        else:
            query = f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL AND "{column_name}" != \'\' ORDER BY "{column_name}"'

        cur.execute(query)
        rows = cur.fetchall()
        raw_values = [row[0] for row in rows]

        cur.close()
        conn.close()

        if not raw_values:
            return {'成功': True, '数据': [], '表名': table_name, '字段名': column_name, '数量': 0}

        return {'成功': True, '数据': raw_values, '表名': table_name, '字段名': column_name, '数量': len(raw_values)}
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


@router.get("/saved-files/{template_id}")
async def get_saved_files(template_id: str, 年月: Optional[str] = None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        formatted_ym = 年月
        if 年月:
            ym_match = re.match(r'^(\d{4})-(\d{1,2})$', 年月)
            if ym_match:
                y, m = ym_match.group(1), ym_match.group(2)
                formatted_ym = f"{y}年{int(m)}月"

        if formatted_ym:
            cursor.execute(
                """SELECT id, 模板名称, 单位名称, 年月, Excel路径, PDF路径, "HTML路径", 保存时间
                   FROM saved_exports WHERE 模板ID = %s AND 年月 = %s
                   ORDER BY 保存时间 DESC""",
                (template_id, formatted_ym)
            )
            rows = cursor.fetchall()
        else:
            cursor.execute(
                """SELECT id, 模板名称, 单位名称, 年月, Excel路径, PDF路径, "HTML路径", 保存时间
                   FROM saved_exports WHERE 模板ID = %s
                   ORDER BY 保存时间 DESC LIMIT 50""",
                (template_id,)
            )
            rows = cursor.fetchall()
        cursor.close()
        conn.close()
        results = []
        for row in rows:
            results.append({
                "ID": row[0],
                "模板名称": row[1],
                "单位名称": row[2],
                "年月": row[3],
                "有Excel": bool(row[4] and os.path.exists(row[4])),
                "有PDF": bool(row[5] and os.path.exists(row[5])),
                "有HTML": bool(row[6] and os.path.exists(row[6])),
                "保存时间": row[7].strftime("%Y-%m-%d %H:%M:%S") if hasattr(row[7], 'strftime') else str(row[7])
            })
        return {"成功": True, "数据": results}
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
        sql = f'SELECT id, 模板名称, 单位名称, 年月, 查询条件, Excel路径, PDF路径, "HTML路径", 保存时间 FROM saved_exports WHERE {where} ORDER BY 保存时间 DESC'
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
                "HTML路径": row[7],
                "保存时间": row[8].strftime("%Y-%m-%d %H:%M:%S") if hasattr(row[8], 'strftime') else str(row[8])
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
async def download_history_file(record_id: int, format: str = "Excel", inline: int = 0):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT Excel路径, PDF路径, "HTML路径" FROM saved_exports WHERE id = %s', (record_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="记录不存在")
        excel_path, pdf_path, html_path = row[0], row[1], row[2]
        if format == "PDF" and pdf_path and os.path.exists(pdf_path):
            response = FileResponse(
                pdf_path,
                filename=os.path.basename(pdf_path),
                media_type="application/pdf"
            )
            if inline:
                response.headers["Content-Disposition"] = "inline"
            return response
        if format == "HTML" and html_path and os.path.exists(html_path):
            return FileResponse(
                html_path,
                media_type="text/html",
                headers={"Content-Disposition": "inline"}
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
