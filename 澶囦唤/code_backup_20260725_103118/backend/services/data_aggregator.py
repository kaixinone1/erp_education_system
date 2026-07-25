from sqlalchemy import create_engine, text
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import json

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education?client_encoding=utf8'
engine = create_engine(DATABASE_URL)

class DataAggregator:
    def __init__(self):
        self.engine = engine
    
    def aggregate_data(self, mappings: List[Dict], fill_type: str, 
                      fill_target: str, teacher_id: Optional[int] = None) -> Dict:
        """
        根据映射配置聚合数据
        
        Args:
            mappings: 字段映射配置列表
            fill_type: 填报类型（unit/personal）
            fill_target: 填报目标（单位名称或个人姓名）
            teacher_id: 教师ID（个人填报时）
        
        Returns:
            {
                "success": True,
                "data": {
                    "C3": "张三",
                    "D3": "男",
                    ...
                }
            }
        """
        try:
            data = {}
            
            for mapping in mappings:
                field_position = mapping["field_position"]
                source_table = mapping["source_table"]
                source_field = mapping["source_field"]
                stat_type = mapping["stat_type"]
                stat_formula = mapping.get("stat_formula")
                
                if fill_type == "personal":
                    value = self._get_personal_data(
                        source_table, source_field, teacher_id, stat_type, stat_formula
                    )
                else:
                    value = self._get_unit_data(
                        source_table, source_field, fill_target, stat_type, stat_formula
                    )
                
                data[field_position] = value
            
            return {
                "success": True,
                "data": data
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_personal_data(self, table: str, field: str, teacher_id: int, 
                           stat_type: str, formula: Optional[str] = None) -> Any:
        """
        获取个人数据
        
        Args:
            table: 数据源表
            field: 目标字段
            teacher_id: 教师ID
            stat_type: 统计方式
            formula: 自定义公式
        
        Returns:
            字段值
        """
        try:
            with self.engine.connect() as conn:
                if table == "教师基础信息表":
                    result = conn.execute(
                        text(f"SELECT {field} FROM teacher_basic_info WHERE 教师ID = :teacher_id"),
                        {"teacher_id": teacher_id}
                    )
                    row = result.fetchone()
                    if row:
                        value = row[0]
                        return self._format_value(value, stat_type)
                
                return None
        
        except Exception as e:
            print(f"获取个人数据失败: {e}")
            return None
    
    def _get_unit_data(self, table: str, field: str, unit_name: str, 
                       stat_type: str, formula: Optional[str] = None) -> Any:
        """
        获取单位数据
        
        Args:
            table: 数据源表
            field: 目标字段
            unit_name: 单位名称
            stat_type: 统计方式
            formula: 自定义公式
        
        Returns:
            统计结果
        """
        try:
            with self.engine.connect() as conn:
                if stat_type == "计数":
                    result = conn.execute(
                        text(f"SELECT COUNT(*) FROM teacher_basic_info WHERE 单位 = :unit_name"),
                        {"unit_name": unit_name}
                    )
                    row = result.fetchone()
                    return row[0] if row else 0
                
                elif stat_type == "求和":
                    result = conn.execute(
                        text(f"SELECT SUM({field}) FROM teacher_basic_info WHERE 单位 = :unit_name"),
                        {"unit_name": unit_name}
                    )
                    row = result.fetchone()
                    return row[0] if row and row[0] else 0
                
                elif stat_type == "平均":
                    result = conn.execute(
                        text(f"SELECT AVG({field}) FROM teacher_basic_info WHERE 单位 = :unit_name"),
                        {"unit_name": unit_name}
                    )
                    row = result.fetchone()
                    return round(row[0], 2) if row and row[0] else 0
                
                else:
                    return None
        
        except Exception as e:
            print(f"获取单位数据失败: {e}")
            return None
    
    def _format_value(self, value: Any, stat_type: str) -> Any:
        """
        格式化值
        
        Args:
            value: 原始值
            stat_type: 统计方式
        
        Returns:
            格式化后的值
        """
        if value is None:
            return None
        
        if stat_type == "格式化日期":
            if isinstance(value, (datetime, date)):
                return value.strftime("%Y年%m月%d日")
        
        elif stat_type == "格式化数字":
            if isinstance(value, (int, float)):
                return round(value, 2)
        
        return value
    
    def search_teachers(self, keyword: str, search_type: str = "姓名") -> Dict:
        """
        搜索教师
        
        Args:
            keyword: 搜索关键词
            search_type: 搜索类型（姓名/身份证/教师ID）
        
        Returns:
            {
                "success": True,
                "teachers": [...]
            }
        """
        try:
            with self.engine.connect() as conn:
                if search_type == "姓名":
                    result = conn.execute(
                        text("SELECT 教师ID, 姓名, 身份证, 单位 FROM teacher_basic_info WHERE 姓名 LIKE :keyword LIMIT 20"),
                        {"keyword": f"%{keyword}%"}
                    )
                elif search_type == "身份证":
                    result = conn.execute(
                        text("SELECT 教师ID, 姓名, 身份证, 单位 FROM teacher_basic_info WHERE 身份证 LIKE :keyword LIMIT 20"),
                        {"keyword": f"%{keyword}%"}
                    )
                else:
                    result = conn.execute(
                        text("SELECT 教师ID, 姓名, 身份证, 单位 FROM teacher_basic_info WHERE CAST(教师ID AS TEXT) LIKE :keyword LIMIT 20"),
                        {"keyword": f"%{keyword}%"}
                    )
                
                teachers = []
                for row in result:
                    teachers.append({
                        "teacher_id": row.教师ID,
                        "name": row.姓名,
                        "id_card": row.身份证,
                        "unit": row.单位
                    })
            
            return {
                "success": True,
                "teachers": teachers
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_units(self) -> Dict:
        """
        获取所有单位列表
        
        Returns:
            {
                "success": True,
                "units": [...]
            }
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT school FROM school_information_table ORDER BY school")
                )
                
                units = [row.school for row in result]
            
            return {
                "success": True,
                "units": units
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
