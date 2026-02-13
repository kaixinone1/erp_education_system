#!/usr/bin/env python3
"""
模板字段映射API - 通用版本
用于管理模板占位符与中间表字段的映射关系
支持自动映射、智能推荐、多格式占位符
"""
from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional
import json
import os
import sys
import psycopg2
from datetime import datetime

# 添加services目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.universal_placeholder_extractor import extract_fields
from services.field_mapping_service import (
    get_table_fields_from_db,
    apply_system_field_names,
    auto_map_fields,
    get_intermediate_tables as get_tables,
    save_field_mapping,
    load_field_mapping,
    load_mapping_config
)

router = APIRouter(prefix="/api/template-field-mapping", tags=["template-field-mapping"])

# 数据库连接配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
SCHEMA_FILE = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')
TABLE_MAPPINGS_FILE = os.path.join(CONFIG_DIR, 'table_name_mappings.json')


def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DATABASE_CONFIG)


def read_json_file(file_path: str) -> dict:
    """读取JSON文件"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return {}


@router.get("/intermediate-tables")
async def get_intermediate_tables():
    """获取所有中间表列表（通用版本）"""
    try:
        # 使用通用服务获取中间表列表
        tables = get_tables()
        
        # 转换为前端期望的格式
        result = []
        for table in tables:
            result.append({
                "name": table.get("name"),
                "name_cn": table.get("label", table.get("name")),
                "type": table.get("type", "intermediate")
            })
        
        return {
            "status": "success",
            "tables": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取中间表列表失败: {str(e)}")


@router.get("/table-fields/{table_name}")
async def get_table_fields(table_name: str):
    """获取指定中间表的所有字段（通用版本）"""
    try:
        # 使用通用服务获取表字段
        fields_data = get_table_fields_from_db(table_name)
        fields_data = apply_system_field_names(fields_data)
        
        # 转换为前端期望的格式
        fields = []
        for field in fields_data:
            fields.append({
                "name": field.get("name"),
                "name_cn": field.get("label", field.get("name")),
                "type": field.get("type", "VARCHAR")
            })
        
        return {
            "status": "success",
            "table_name": table_name,
            "table_name_cn": table_name,
            "fields": fields
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取表字段失败: {str(e)}")


@router.get("/template-placeholders/{template_id}")
async def get_template_placeholders(template_id: str):
    """获取模板中的所有占位符（通用版本）"""
    try:
        # 尝试将template_id转换为整数
        try:
            template_id_int = int(template_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的模板ID: {template_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 从document_templates表获取模板内容
        cursor.execute("""
            SELECT template_name, file_path 
            FROM document_templates 
            WHERE id = %s
        """, (template_id_int,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        template_name, file_path = row
        
        # 使用通用占位符提取服务
        placeholders = []
        if file_path and os.path.exists(file_path):
            try:
                # 获取文件扩展名
                file_ext = os.path.splitext(file_path)[1].lower()
                # 使用通用提取器
                fields = extract_fields(file_path, file_ext)
                
                # 去重并转换为前端格式
                seen = set()
                for field in fields:
                    name = field.get('name', '')
                    if name and name not in seen:
                        seen.add(name)
                        placeholders.append({
                            "name": name,
                            "name_cn": field.get('label', name)
                        })
            except Exception as e:
                print(f"解析模板文件失败: {e}")
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "template_id": template_id,
            "template_name": template_name,
            "placeholders": placeholders
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板占位符失败: {str(e)}")


@router.post("/save-mapping")
async def save_field_mapping(data: dict = Body(...)):
    """保存字段映射关系（增量更新）"""
    try:
        template_id = data.get("template_id")
        template_name = data.get("template_name")
        intermediate_table = data.get("intermediate_table")
        intermediate_table_cn = data.get("intermediate_table_cn")
        mappings = data.get("mappings", [])  # [{placeholder, field, field_cn}, ...]
        
        if not template_id or not intermediate_table:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取现有映射
        cursor.execute("""
            SELECT placeholder_name, intermediate_field
            FROM template_field_mapping
            WHERE template_id = %s
        """, (template_id,))
        
        existing_mappings = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 统计变更
        updated_count = 0
        inserted_count = 0
        unchanged_count = 0
        
        for mapping in mappings:
            placeholder = mapping.get("placeholder")
            field = mapping.get("field")
            field_cn = mapping.get("field_cn")
            
            if placeholder in existing_mappings:
                if existing_mappings[placeholder] != field:
                    # 更新现有映射
                    cursor.execute("""
                        UPDATE template_field_mapping
                        SET intermediate_table = %s,
                            intermediate_table_cn = %s,
                            intermediate_field = %s,
                            intermediate_field_cn = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE template_id = %s AND placeholder_name = %s
                    """, (
                        intermediate_table,
                        intermediate_table_cn,
                        field,
                        field_cn,
                        template_id,
                        placeholder
                    ))
                    updated_count += 1
                else:
                    unchanged_count += 1
            else:
                # 插入新映射
                cursor.execute("""
                    INSERT INTO template_field_mapping 
                    (template_id, template_name, placeholder_name, 
                     intermediate_table, intermediate_table_cn,
                     intermediate_field, intermediate_field_cn)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    template_id,
                    template_name,
                    placeholder,
                    intermediate_table,
                    intermediate_table_cn,
                    field,
                    field_cn
                ))
                inserted_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"保存完成：新增 {inserted_count} 个，更新 {updated_count} 个，未变更 {unchanged_count} 个"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存映射失败: {str(e)}")


@router.get("/get-mapping/{template_id}")
async def get_field_mapping(template_id: str):
    """获取模板的字段映射关系"""
    try:
        # 尝试将template_id转换为整数
        try:
            template_id_int = int(template_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的模板ID: {template_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, template_id, template_name, placeholder_name,
                   intermediate_table, intermediate_table_cn,
                   intermediate_field, intermediate_field_cn, is_active
            FROM template_field_mapping
            WHERE template_id = %s
            ORDER BY id
        """, (template_id_int,))
        
        rows = cursor.fetchall()
        
        mappings = []
        intermediate_table = ""
        intermediate_table_cn = ""
        
        for row in rows:
            mappings.append({
                "id": row[0],
                "placeholder": row[3],
                "field": row[6],
                "field_cn": row[7],
                "is_active": row[8]
            })
            if not intermediate_table:
                intermediate_table = row[4]
                intermediate_table_cn = row[5]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "template_id": template_id,
            "intermediate_table": intermediate_table,
            "intermediate_table_cn": intermediate_table_cn,
            "mappings": mappings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取映射失败: {str(e)}")


@router.get("/fill-data/{template_id}")
async def get_fill_data(template_id: str, teacher_id: int):
    """获取填报数据（根据模板映射和教师ID）"""
    try:
        # 尝试将template_id转换为整数
        try:
            template_id_int = int(template_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的模板ID: {template_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 获取模板的字段映射
        cursor.execute("""
            SELECT placeholder_name, intermediate_table, intermediate_field
            FROM template_field_mapping
            WHERE template_id = %s AND is_active = TRUE
        """, (template_id_int,))
        
        mappings = cursor.fetchall()
        if not mappings:
            raise HTTPException(status_code=404, detail="该模板未配置字段映射")
        
        # 2. 获取中间表名
        intermediate_table = mappings[0][1]
        
        # 3. 构建查询字段
        fields = [m[2] for m in mappings]
        field_list = ', '.join(fields)
        
        # 4. 从中间表查询该教师的数据
        cursor.execute(f"""
            SELECT {field_list}
            FROM {intermediate_table}
            WHERE teacher_id = %s
            LIMIT 1
        """, (teacher_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="未找到该教师的数据")
        
        # 5. 构建返回数据（占位符 -> 值）
        data = {}
        for i, mapping in enumerate(mappings):
            placeholder = mapping[0]
            value = row[i] if i < len(row) else None
            data[placeholder] = value
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "template_id": template_id,
            "teacher_id": teacher_id,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取填报数据失败: {str(e)}")


@router.get("/preview/{template_id}")
async def preview_template_with_mapping(template_id: str, teacher_id: int = 0, mode: str = "fill", debug: bool = False):
    """预览填充后的模板（使用字段映射配置）
    
    参数:
        template_id: 模板ID
        teacher_id: 教师ID（mode=fill时必填，mode=preview时可选）
        mode: 模式，fill=填报模式（填充数据），preview=预览模式（保留占位符）
        debug: 是否返回调试信息（替换统计）
    """
    try:
        # 打印调试信息
        print(f"【API】preview_template_with_mapping called: template_id={template_id}, teacher_id={teacher_id}, mode={mode}")
        
        # 使用新的占位符模板引擎
        from services.placeholder_template_engine import PlaceholderTemplateEngine
        engine = PlaceholderTemplateEngine(get_db_connection)
        
        # 根据模式生成文档
        if mode == "preview":
            # 预览模式：返回原始模板，不填充数据
            html_content = engine.get_raw_template(template_id)
        else:
            # 填报模式：填充数据
            print(f"【API】生成文档: template_id={template_id}, teacher_id={teacher_id}")
            html_content = engine.generate_document(template_id, teacher_id)
            print(f"【API】文档生成完成，长度={len(html_content)}")
        
        # 如果需要调试信息，返回JSON格式
        if debug and mode == "fill":
            import re
            import json
            
            # 获取模板配置
            config = engine.get_field_mapping(template_id)
            
            # 读取原始模板
            raw_html = engine.get_raw_template(template_id)
            
            # 提取所有占位符
            all_placeholders = re.findall(r'\{\{([^{}]+)\}\}', raw_html)
            all_placeholders = [p.strip() for p in all_placeholders]
            total_placeholders = len(all_placeholders)
            unique_placeholders = list(set(all_placeholders))
            
            # 检查哪些占位符已被替换
            remaining = re.findall(r'\{\{([^{}]+)\}\}', html_content)
            remaining = [p.strip() for p in remaining]
            remaining_unique = list(set(remaining))
            
            # 计算替换统计
            replaced_count = total_placeholders - len(remaining)
            replaced_unique = len(unique_placeholders) - len(remaining_unique)
            
            # 获取字段映射信息
            mapping_info = {}
            for mapping in config.get('mappings', []):
                placeholder = mapping['placeholder'].strip()
                if placeholder.startswith('{{') and placeholder.endswith('}}'):
                    placeholder = placeholder[2:-2]
                elif placeholder.startswith('{') and placeholder.endswith('}'):
                    placeholder = placeholder[1:-1]
                mapping_info[placeholder] = {
                    'table': mapping.get('table', ''),
                    'field': mapping.get('field', '')
                }
            
            # 构建未替换占位符的详细信息
            unmapped_details = []
            for p in remaining_unique:
                info = mapping_info.get(p, {})
                unmapped_details.append({
                    'placeholder': p,
                    'mapped': p in mapping_info,
                    'table': info.get('table', ''),
                    'field': info.get('field', '')
                })
            
            debug_info = {
                'status': 'success',
                'template_id': template_id,
                'teacher_id': teacher_id,
                'statistics': {
                    'total_placeholders': total_placeholders,
                    'unique_placeholders': len(unique_placeholders),
                    'replaced_count': replaced_count,
                    'replaced_unique': replaced_unique,
                    'remaining_count': len(remaining),
                    'remaining_unique': len(remaining_unique),
                    'replacement_rate': f"{replaced_unique}/{len(unique_placeholders)} ({replaced_unique/len(unique_placeholders)*100:.1f}%)" if unique_placeholders else "N/A"
                },
                'all_placeholders': unique_placeholders,
                'unmapped_placeholders': unmapped_details,
                'html_preview': html_content[:2000] + '...' if len(html_content) > 2000 else html_content
            }
            
            return debug_info
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")


@router.post("/preview-with-data/{template_id}")
async def preview_with_override_data(template_id: str, request: dict = Body(...)):
    """使用覆盖数据预览模板"""
    try:
        teacher_id = request.get("teacher_id", 0)
        override_data = request.get("override_data", {})
        
        # 使用新的占位符模板引擎
        from services.placeholder_template_engine import PlaceholderTemplateEngine
        engine = PlaceholderTemplateEngine(get_db_connection)
        
        # 获取模板配置
        config = engine.get_field_mapping(template_id)
        template_path = config['file_path']
        mappings = config['mappings']
        
        if not os.path.exists(template_path):
            raise ValueError(f"模板文件不存在: {template_path}")
        
        # 获取基础数据
        base_data = {}
        for mapping in mappings:
            placeholder = mapping['placeholder']
            table = mapping['table']
            field = mapping['field']
            value = engine.get_data_from_table(table, field, teacher_id)
            base_data[placeholder] = value
        
        # 使用覆盖数据更新
        base_data.update(override_data)
        
        # 读取模板文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
        content = None
        for encoding in encodings:
            try:
                with open(template_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    break
            except:
                continue
        
        if not content:
            raise ValueError("无法读取模板文件")
        
        # 替换占位符
        import re
        for placeholder, value in base_data.items():
            pattern = r'\{\{' + re.escape(placeholder) + r'\}\}'
            content = re.sub(pattern, value, content)
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=content)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")


@router.post("/save-html/{template_id}")
async def save_html_content(template_id: str, request: dict = Body(...)):
    """
    保存编辑后的HTML内容
    将编辑后的内容保存为新的模板文件或覆盖原文件
    """
    try:
        teacher_id = request.get("teacher_id", 0)
        html_content = request.get("html_content", "")
        
        if not html_content:
            raise HTTPException(status_code=400, detail="HTML内容不能为空")
        
        # 获取模板信息
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 获取模板基本信息（支持id或template_id查询）
            template_row = None
            
            # 先尝试用id查询（如果是数字）
            try:
                id_int = int(template_id)
                cursor.execute("""
                    SELECT id, template_id, template_name, file_path
                    FROM document_templates
                    WHERE id = %s
                """, (id_int,))
                template_row = cursor.fetchone()
            except ValueError:
                pass  # 不是数字，继续用template_id查询
            
            # 如果没找到，尝试用template_id字段查询
            if not template_row:
                cursor.execute("""
                    SELECT id, template_id, template_name, file_path
                    FROM document_templates
                    WHERE template_id = %s
                """, (str(template_id),))
                template_row = cursor.fetchone()
            
            if not template_row:
                raise HTTPException(status_code=404, detail=f"模板不存在: {template_id}")
            
            actual_template_id = template_row[0]
            template_name = template_row[2]
            original_file_path = template_row[3]
            
            # 直接覆盖原文件
            import os
            
            if original_file_path and os.path.exists(original_file_path):
                # 覆盖原文件
                file_path = original_file_path
            else:
                # 如果原文件路径不存在，使用默认路径
                save_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
                file_path = os.path.join(save_dir, template_name)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 写入文件（覆盖原文件）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                "status": "success",
                "message": "保存成功",
                "file_name": template_name,
                "file_path": file_path
            }
            
        finally:
            cursor.close()
            conn.close()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
