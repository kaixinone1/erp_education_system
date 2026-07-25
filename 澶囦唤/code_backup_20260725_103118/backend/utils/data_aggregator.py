#!/usr/bin/env python3
"""
通用数据聚合组件
用于从多个源表获取数据，通过代理主键关联，自动处理字典转换，生成目标表数据
"""
import psycopg2
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class FieldType(Enum):
    """字段类型"""
    DIRECT = "direct"           # 直接取值
    DICT = "dict"               # 字典转换
    CALCULATED = "calculated"   # 计算字段
    DEFAULT = "default"         # 默认值


@dataclass
class FieldMapping:
    """字段映射配置"""
    target_field: str           # 目标字段名
    source_table: str           # 源表名
    source_field: str           # 源字段名（可以是多个字段，用逗号分隔）
    field_type: FieldType = FieldType.DIRECT
    source_key_field: str = "teacher_id"  # 源表关联字段名
    dict_table: Optional[str] = None      # 字典表名（用于字典类型）
    dict_code_field: Optional[str] = None # 字典代码字段
    dict_name_field: Optional[str] = None # 字典名称字段
    default_value: Any = None   # 默认值
    transform_func: Optional[Callable] = None  # 转换函数，接收整行数据


@dataclass
class AggregationConfig:
    """数据聚合配置"""
    target_table: str           # 目标表名
    primary_key: str            # 代理主键字段名（如 teacher_id）
    mappings: List[FieldMapping]  # 字段映射列表


class DataAggregator:
    """通用数据聚合器"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self._dict_cache = {}  # 字典缓存
    
    def _get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(**self.db_config)
    
    def _get_dict_name(self, dict_table: str, code_field: str, 
                       name_field: str, code_value: Any) -> Optional[str]:
        """从字典表获取名称"""
        if code_value is None:
            return None
        
        # 构建缓存键
        cache_key = f"{dict_table}:{code_field}:{code_value}"
        if cache_key in self._dict_cache:
            return self._dict_cache[cache_key]
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"""
                SELECT {name_field} 
                FROM {dict_table} 
                WHERE {code_field} = %s
            """
            cursor.execute(query, (code_value,))
            row = cursor.fetchone()
            result = row[0] if row else None
            
            # 缓存结果
            self._dict_cache[cache_key] = result
            return result
            
        finally:
            cursor.close()
            conn.close()
    
    def _get_source_value(self, cursor, primary_key_value: int, 
                          mapping: FieldMapping) -> Any:
        """从源表获取字段值"""
        if mapping.field_type == FieldType.DEFAULT:
            return mapping.default_value
        
        # 查询源表
        query = f"""
            SELECT {mapping.source_field}
            FROM {mapping.source_table}
            WHERE {mapping.source_key_field} = %s
            ORDER BY id DESC
            LIMIT 1
        """
        cursor.execute(query, (primary_key_value,))
        row = cursor.fetchone()
        
        if not row:
            return mapping.default_value
        
        # 计算字段 - 使用整行数据进行计算
        if mapping.field_type == FieldType.CALCULATED and mapping.transform_func:
            return mapping.transform_func(row)
        
        # 普通字段处理
        value = row[0]
        
        if value is None:
            return mapping.default_value
        
        # 字典转换
        if mapping.field_type == FieldType.DICT and mapping.dict_table:
            value = self._get_dict_name(
                mapping.dict_table,
                mapping.dict_code_field or 'id',
                mapping.dict_name_field or 'name',
                value
            )
        
        # 自定义转换
        if mapping.transform_func:
            value = mapping.transform_func(value)
        
        return value
    
    def aggregate(self, config: AggregationConfig, 
                  primary_key_value: int) -> Dict[str, Any]:
        """
        执行数据聚合
        
        Args:
            config: 聚合配置
            primary_key_value: 代理主键值
            
        Returns:
            聚合后的数据字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            result = {config.primary_key: primary_key_value}
            
            for mapping in config.mappings:
                value = self._get_source_value(cursor, primary_key_value, mapping)
                result[mapping.target_field] = value
            
            return result
            
        finally:
            cursor.close()
            conn.close()
    
    def save_to_target(self, config: AggregationConfig, 
                       data: Dict[str, Any]) -> bool:
        """
        保存数据到目标表
        
        Args:
            config: 聚合配置
            data: 数据字典
            
        Returns:
            是否成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 构建 INSERT 语句
            fields = list(data.keys())
            values = list(data.values())
            
            field_str = ', '.join(fields)
            placeholder_str = ', '.join(['%s'] * len(fields))
            
            # 构建 ON CONFLICT 更新语句
            updates = [f"{f} = EXCLUDED.{f}" for f in fields if f != config.primary_key]
            update_str = ', '.join(updates)
            
            query = f"""
                INSERT INTO {config.target_table} ({field_str})
                VALUES ({placeholder_str})
                ON CONFLICT ({config.primary_key}) DO UPDATE
                SET {update_str}
            """
            
            cursor.execute(query, values)
            conn.commit()
            return True
            
        except Exception as e:
            print(f"保存数据失败: {e}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            conn.close()


# 预定义的字段映射配置
class PredefinedConfigs:
    """预定义的配置"""
    
    @staticmethod
    def retirement_report_config() -> AggregationConfig:
        """退休呈报表数据聚合配置"""
        return AggregationConfig(
            target_table="retirement_report_data",
            primary_key="teacher_id",
            mappings=[
                # 基础信息 - 从 teacher_basic_info 表获取（使用 id 作为关联字段）
                FieldMapping("姓名", "teacher_basic_info", "name", source_key_field="id"),
                FieldMapping("身份证号码", "teacher_basic_info", "id_card", source_key_field="id"),
                # 出生日期使用计算字段，优先档案出生日期，否则从身份证提取
                FieldMapping(
                    "出生日期", "teacher_basic_info", "archive_birth_date, id_card",
                    field_type=FieldType.CALCULATED,
                    source_key_field="id",
                    transform_func=lambda row: row[0] if row[0] else (f"{row[1][6:10]}-{row[1][10:12]}-{row[1][12:14]}" if row[1] and len(row[1]) == 18 else None)
                ),
                FieldMapping("民族", "teacher_basic_info", "ethnicity", source_key_field="id"),
                FieldMapping("籍贯", "teacher_basic_info", "native_place", source_key_field="id"),
                FieldMapping("参加工作时间", "teacher_basic_info", "work_start_date", source_key_field="id"),
                
                # 学历信息 - 从 teacher_education_record 表获取，并转换字典
                FieldMapping(
                    "文化程度", "teacher_education_record", "education",
                    field_type=FieldType.DICT,
                    dict_table="dict_education_level_dictionary",
                    dict_code_field="id",
                    dict_name_field="education"
                ),
                
                # 默认值字段
                FieldMapping("工作年限", "", "", field_type=FieldType.DEFAULT, default_value=0),
            ]
        )


# 便捷函数
def aggregate_retirement_data(teacher_id: int, db_config: Dict[str, str]) -> Dict[str, Any]:
    """
    聚合退休呈报表数据
    
    Args:
        teacher_id: 教师ID
        db_config: 数据库配置
        
    Returns:
        聚合后的数据
    """
    aggregator = DataAggregator(db_config)
    config = PredefinedConfigs.retirement_report_config()
    return aggregator.aggregate(config, teacher_id)


def save_retirement_data(teacher_id: int, db_config: Dict[str, str]) -> bool:
    """
    聚合并保存退休呈报表数据
    
    Args:
        teacher_id: 教师ID
        db_config: 数据库配置
        
    Returns:
        是否成功
    """
    aggregator = DataAggregator(db_config)
    config = PredefinedConfigs.retirement_report_config()
    data = aggregator.aggregate(config, teacher_id)
    return aggregator.save_to_target(config, data)
