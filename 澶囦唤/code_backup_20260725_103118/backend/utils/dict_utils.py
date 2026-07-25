#!/usr/bin/env python3
"""字典表查询工具 - 通用字典表查询机制"""
import psycopg2
from typing import Optional, Dict, Any

# 字典表配置映射
DICT_TABLE_MAPPINGS = {
    'education': {
        'table': 'dict_education_level_dictionary',
        'code_field': 'id',
        'name_field': 'education'
    },
    'education_type': {
        'table': 'dict_education_type_dictionary',
        'code_field': 'id',
        'name_field': 'type_name'
    }
}


def get_dict_name(dict_type: str, code: Any, db_config: Dict[str, str]) -> Optional[str]:
    """
    根据字典类型和代码获取中文名称
    
    Args:
        dict_type: 字典类型，如 'education'
        code: 代码值，如 6
        db_config: 数据库配置
        
    Returns:
        中文名称，如 '本科'，如果没有找到返回 None
    """
    if code is None:
        return None
    
    if dict_type not in DICT_TABLE_MAPPINGS:
        return None
    
    config = DICT_TABLE_MAPPINGS[dict_type]
    
    try:
        conn = psycopg2.connect(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', '5432'),
            database=db_config.get('database', 'taiping_education'),
            user=db_config.get('user', 'taiping_user'),
            password=db_config.get('password', 'taiping_password')
        )
        cursor = conn.cursor()
        
        query = f"""
            SELECT {config['name_field']} 
            FROM {config['table']} 
            WHERE {config['code_field']} = %s
        """
        cursor.execute(query, (code,))
        
        row = cursor.fetchone()
        result = row[0] if row else None
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        print(f"查询字典表失败: {e}")
        return None


def get_education_name(education_code: int, db_config: Dict[str, str]) -> Optional[str]:
    """
    获取学历中文名称
    
    Args:
        education_code: 学历代码，如 6
        db_config: 数据库配置
        
    Returns:
        学历中文名称，如 '本科'
    """
    return get_dict_name('education', education_code, db_config)
