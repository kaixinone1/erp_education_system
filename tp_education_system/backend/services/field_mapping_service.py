"""
通用字段映射服务
支持模板占位符与中间表字段的自动映射和手动配置
"""
import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
import psycopg2

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'field_mapping_config.json')
TABLE_NAME_CN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'table_name_cn.json')


def load_mapping_config() -> Dict[str, Any]:
    """加载字段映射配置"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载字段映射配置失败: {e}")
        return {
            "mapping_types": {"direct": {"name": "直接映射"}},
            "auto_mapping_rules": [],
            "common_fields": {}
        }


def load_table_name_cn() -> Dict[str, str]:
    """加载表名中文映射"""
    try:
        with open(TABLE_NAME_CN_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("table_name_mappings", {})
    except Exception as e:
        print(f"加载表名中文映射失败: {e}")
        return {}


def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )


def get_table_fields_from_db(table_name: str) -> List[Dict[str, Any]]:
    """从数据库获取表字段"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        fields = []
        for row in cursor.fetchall():
            col_name, data_type, is_nullable = row
            fields.append({
                "name": col_name,
                "label": col_name,  # 默认使用字段名
                "type": data_type,
                "required": is_nullable == "NO"
            })
        
        return fields
    finally:
        cursor.close()
        conn.close()


def apply_system_field_names(fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """应用系统字段中文名"""
    config = load_mapping_config()
    system_fields = config.get("common_fields", {})
    
    for field in fields:
        field_name = field.get("name", "")
        if field_name in system_fields:
            field["label"] = system_fields[field_name].get("label", field_name)
            field["is_system"] = True
    
    return fields


def suggest_field_mapping(placeholder: str, available_fields: List[Dict[str, Any]]) -> Optional[str]:
    """
    根据占位符名称智能推荐匹配的字段
    使用配置中的自动映射规则
    """
    config = load_mapping_config()
    rules = config.get("auto_mapping_rules", [])
    
    # 按优先级排序规则
    rules = sorted(rules, key=lambda x: x.get("priority", 999))
    
    for rule in rules:
        pattern = rule.get("placeholder_pattern", "")
        candidates = rule.get("field_candidates", [])
        
        # 检查占位符是否匹配规则
        if pattern in placeholder or re.search(pattern, placeholder, re.IGNORECASE):
            # 在可用字段中查找候选字段
            for candidate in candidates:
                for field in available_fields:
                    if field.get("name") == candidate or field.get("label") == candidate:
                        return field.get("name")
    
    # 如果没有匹配的规则，尝试模糊匹配
    placeholder_lower = placeholder.lower()
    for field in available_fields:
        field_name = field.get("name", "").lower()
        field_label = field.get("label", "").lower()
        
        # 完全匹配
        if placeholder_lower == field_name or placeholder_lower == field_label:
            return field.get("name")
        
        # 包含关系
        if placeholder_lower in field_name or placeholder_lower in field_label:
            return field.get("name")
        if field_name in placeholder_lower or field_label in placeholder_lower:
            return field.get("name")
    
    return None


def auto_map_fields(
    placeholders: List[str],
    table_name: str
) -> List[Dict[str, Any]]:
    """
    自动映射占位符到表字段
    返回映射关系列表
    """
    # 获取表字段
    table_fields = get_table_fields_from_db(table_name)
    table_fields = apply_system_field_names(table_fields)
    
    mappings = []
    for placeholder in placeholders:
        suggested_field = suggest_field_mapping(placeholder, table_fields)
        
        mapping = {
            "placeholder": placeholder,
            "field": suggested_field,
            "field_label": next((f.get("label") for f in table_fields if f.get("name") == suggested_field), None) if suggested_field else None,
            "confidence": "high" if suggested_field else "none",
            "mapping_type": "direct"
        }
        mappings.append(mapping)
    
    return mappings


def validate_mapping(
    placeholder: str,
    field_name: str,
    field_type: str
) -> Tuple[bool, str]:
    """
    验证映射是否有效
    返回 (是否有效, 错误信息)
    """
    if not placeholder:
        return False, "占位符不能为空"
    
    if not field_name:
        return False, "字段名不能为空"
    
    # 检查类型兼容性
    # 这里可以添加更多类型检查逻辑
    
    return True, ""


def get_source_tables() -> List[Dict[str, Any]]:
    """获取所有可用的源数据表列表（带中文名）- 不包括中间表、字典表、系统表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 预设的源数据表中文名称
        source_table_names = {
            'teacher_basic_info': '教师基础信息',
            'teacher_education_record': '教师学历信息',
            'teacher_training_records': '教师培训记录',
            'retirement_report_form': '退休呈报表',
            'retirement_cert_records': '退休证记录',
            'performance_pay_approval': '绩效工资审批',
            'business_checklist': '业务清单',
            'navigation_modules': '导航模块',
            'todo_work': '待办工作',
        }
        
        # 需要排除的表名模式
        exclude_prefixes = ['pg_', 'sql_', 'dict_', 'template_']
        exclude_tables = [
            'intermediate_tables', 
            'document_templates', 
            'template_field_mapping',
            'template_usage_records',
            'template_field_mappings',
            'template_page_settings',
            'template_placeholders',
            'template_regions'
        ]
        
        # 获取已定义的中间表（需要排除）
        cursor.execute("SELECT table_name FROM intermediate_tables")
        for row in cursor.fetchall():
            exclude_tables.append(row[0])
        
        # 从数据库获取所有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = []
        for row in cursor.fetchall():
            table_name = row[0]
            
            # 过滤掉：前缀匹配
            if any(table_name.startswith(prefix) for prefix in exclude_prefixes):
                continue
            # 过滤掉：精确匹配
            if table_name in exclude_tables:
                continue
            
            # 获取中文名
            cn_name = source_table_names.get(table_name, table_name)
            
            tables.append({
                "name": table_name,
                "name_cn": cn_name,
                "label": cn_name,
                "type": "source"
            })
        
        return tables
    finally:
        cursor.close()
        conn.close()


def get_intermediate_tables() -> List[Dict[str, Any]]:
    """获取所有可用的中间表列表（带中文名）- 兼容旧版本"""
    # 调用新的源数据表函数
    return get_source_tables()


def save_field_mapping(
    template_id: str,
    mappings: List[Dict[str, Any]],
    intermediate_table: str
) -> bool:
    """保存字段映射关系到数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 删除旧的映射
        cursor.execute("""
            DELETE FROM template_field_mapping
            WHERE template_id = %s
        """, (template_id,))
        
        # 插入新的映射
        for mapping in mappings:
            cursor.execute("""
                INSERT INTO template_field_mapping
                (template_id, placeholder_name, intermediate_table, intermediate_field, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                template_id,
                mapping.get("placeholder"),
                intermediate_table,
                mapping.get("field"),
                mapping.get("is_active", True)
            ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"保存字段映射失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def load_field_mapping(template_id: str) -> List[Dict[str, Any]]:
    """从数据库加载字段映射关系"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT placeholder_name, intermediate_table, intermediate_field, is_active
            FROM template_field_mapping
            WHERE template_id = %s
            ORDER BY id
        """, (template_id,))
        
        mappings = []
        for row in cursor.fetchall():
            mappings.append({
                "placeholder": row[0],
                "intermediate_table": row[1],
                "field": row[2],
                "is_active": row[3]
            })
        
        return mappings
    finally:
        cursor.close()
        conn.close()
