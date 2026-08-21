#!/usr/bin/env python3
"""
数据填报引擎 - 根据字段映射配置自动从数据库获取数据并填充
核心功能：解析字段映射、动态生成SQL、支持聚合函数、数据格式转换
"""
import copy
from typing import Dict, List, Any
from core.dynamic_db import DynamicTableManager, engine

class DataFillEngine:
    """
    数据填报引擎 - 负责根据字段映射自动从数据库查询并填充数据
    """
    
    def __init__(self):
        self.db = DynamicTableManager()
    
    def fill_template_data(self, config: Dict[str, Any], query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动填报数据
        
        Args:
            config: 模板JSON配置（包含字段映射）
            query_params: 查询条件（如职工ID、年月等）
            
        Returns:
            填充后的JSON数据
        """
        filled_data = copy.deepcopy(config)
        
        # 遍历所有字段映射
        field_mappings = config.get("field_mappings", {})
        for field_name, mapping in field_mappings.items():
            try:
                # 解析数据源
                if "data_source" in mapping:
                    table, column = mapping["data_source"].split(".")
                    
                    # 根据映射类型执行不同查询
                    if mapping.get("aggregate_func"):
                        value = self._execute_aggregate_query(
                            table, column, 
                            mapping["aggregate_func"], 
                            query_params
                        )
                    else:
                        value = self._execute_select_query(table, column, query_params)
                    
                    # 应用转换函数
                    if mapping.get("transform_func"):
                        value = self._apply_transform(mapping["transform_func"], value)
                    
                    # 填充到对应单元格
                    self._fill_cell_value(filled_data, mapping, value)
                elif mapping.get("default_value"):
                    # 使用默认值
                    self._fill_cell_value(filled_data, mapping, mapping["default_value"])
                    
            except Exception as e:
                print(f"填充字段 {field_name} 失败: {e}")
                # 使用默认值或空值
                default_val = mapping.get("default_value", "")
                self._fill_cell_value(filled_data, mapping, default_val)
        
        return filled_data
    
    def _execute_select_query(self, table: str, column: str, query_params: Dict[str, Any]) -> str:
        """
        执行单值查询
        
        Args:
            table: 表名
            column: 字段名
            query_params: 查询条件
            
        Returns:
            查询结果值
        """
        # 构建WHERE条件
        conditions = {k: v for k, v in query_params.items() if v is not None and v != ""}
        
        if not conditions:
            return ""
        
        try:
            # 使用select方法查询
            results = self.db.select(table, conditions)
            if results and len(results) > 0:
                return str(results[0].get(column, ""))
        except Exception as e:
            print(f"查询失败 {table}.{column}: {e}")
        
        return ""
    
    def _execute_aggregate_query(self, table: str, column: str, 
                                 aggregate_func: str, query_params: Dict[str, Any]) -> str:
        """
        执行聚合函数查询
        
        Args:
            table: 表名
            column: 字段名
            aggregate_func: 聚合函数（COUNT, SUM, AVG, MAX, MIN）
            query_params: 查询条件
            
        Returns:
            聚合结果
        """
        valid_funcs = ["COUNT", "SUM", "AVG", "MAX", "MIN"]
        func_upper = aggregate_func.upper()
        
        if func_upper not in valid_funcs:
            print(f"无效的聚合函数: {aggregate_func}")
            return ""
        
        # 构建WHERE条件
        where_clauses = []
        params = {}
        
        for key, value in query_params.items():
            if value is not None and value != "":
                where_clauses.append(f"{key} = %s")
                params[key] = value
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        if func_upper == "COUNT":
            sql = f"SELECT COUNT(*) FROM {table} WHERE {where_sql}"
        else:
            sql = f"SELECT {func_upper}({column}) FROM {table} WHERE {where_sql}"
        
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text(sql), params)
                val = result.scalar()
                if func_upper in ["AVG"]:
                    return str(round(float(val), 2)) if val else "0"
                return str(val) if val else "0"
        except Exception as e:
            print(f"聚合查询失败 {aggregate_func}({table}.{column}): {e}")
        
        return "0"
    
    def _apply_transform(self, transform_func: str, value: str) -> str:
        """
        应用转换函数
        
        Args:
            transform_func: 转换函数名称
            value: 原始值
            
        Returns:
            转换后的值
        """
        try:
            if transform_func == "format_date":
                return self._format_date(value)
            elif transform_func == "format_currency":
                return self._format_currency(value)
            elif transform_func == "format_number":
                return self._format_number(value)
            elif transform_func == "format_percent":
                return self._format_percent(value)
            elif transform_func == "to_upper":
                return value.upper()
            elif transform_func == "to_lower":
                return value.lower()
            elif transform_func.startswith("substring"):
                # substring(start, length)
                parts = transform_func.split("(")[1].rstrip(")").split(",")
                start = int(parts[0].strip())
                length = int(parts[1].strip()) if len(parts) > 1 else len(value)
                return value[start-1:start-1+length]
            else:
                print(f"未知的转换函数: {transform_func}")
        except Exception as e:
            print(f"转换失败 {transform_func}({value}): {e}")
        
        return value
    
    def _format_date(self, value: str) -> str:
        """格式化日期为中文格式"""
        try:
            from datetime import datetime
            if value:
                formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", 
                          "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]
                for fmt in formats:
                    try:
                        dt = datetime.strptime(value, fmt)
                        return f"{dt.year}年{dt.month}月{dt.day}日"
                    except ValueError:
                        continue
        except Exception as e:
            print(f"日期格式化失败: {e}")
        
        return value
    
    def _format_currency(self, value: str) -> str:
        """格式化货币"""
        try:
            if value:
                return f"{float(value):,.2f}"
        except Exception as e:
            print(f"货币格式化失败: {e}")
        
        return value
    
    def _format_number(self, value: str) -> str:
        """格式化数字"""
        try:
            if value:
                return f"{int(float(value)):,}"
        except Exception as e:
            print(f"数字格式化失败: {e}")
        
        return value
    
    def _format_percent(self, value: str) -> str:
        """格式化百分比"""
        try:
            if value:
                return f"{float(value) * 100:.2f}%"
        except Exception as e:
            print(f"百分比格式化失败: {e}")
        
        return value
    
    def _fill_cell_value(self, config: Dict[str, Any], mapping: Dict[str, Any], value: str):
        """
        填充单元格值
        
        Args:
            config: 模板配置
            mapping: 字段映射配置
            value: 要填充的值
        """
        row_num = mapping.get("row", mapping.get("row_number"))
        col_num = mapping.get("column", mapping.get("column_number"))
        
        if row_num and col_num:
            try:
                row_idx = row_num - 1
                col_idx = col_num - 1
                
                if row_idx < len(config["rows"]):
                    row = config["rows"][row_idx]
                    if col_idx < len(row["cells"]):
                        row["cells"][col_idx]["text"] = value
            except Exception as e:
                print(f"填充单元格失败 (行{row_num}, 列{col_num}): {e}")
    
    def batch_fill(self, config: Dict[str, Any], query_params_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量填报数据
        
        Args:
            config: 模板JSON配置
            query_params_list: 查询条件列表
            
        Returns:
            填充后的JSON数据列表
        """
        results = []
        
        for params in query_params_list:
            filled = self.fill_template_data(config, params)
            results.append(filled)
        
        return results
    
    def validate_mappings(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        验证字段映射配置
        
        Args:
            config: 模板JSON配置
            
        Returns:
            验证错误列表
        """
        errors = []
        field_mappings = config.get("field_mappings", {})
        
        for field_name, mapping in field_mappings.items():
            if "data_source" not in mapping and "default_value" not in mapping:
                errors.append({
                    "field": field_name,
                    "error": "缺少数据源或默认值配置"
                })
            
            if "data_source" in mapping:
                ds = mapping["data_source"]
                if "." not in ds:
                    errors.append({
                        "field": field_name,
                        "error": f"数据源格式错误: {ds}，正确格式应为 表名.字段名"
                    })
                else:
                    table, column = ds.split(".", 1)
                    if not self._check_table_exists(table):
                        errors.append({
                            "field": field_name,
                            "error": f"数据表不存在: {table}"
                        })
            
            if mapping.get("aggregate_func"):
                func = mapping["aggregate_func"].upper()
                if func not in ["COUNT", "SUM", "AVG", "MAX", "MIN"]:
                    errors.append({
                        "field": field_name,
                        "error": f"无效的聚合函数: {mapping['aggregate_func']}"
                    })
        
        return errors
    
    def _check_table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            return self.db.get_table_exists(table_name)
        except Exception as e:
            print(f"检查表存在失败 {table_name}: {e}")
            return False

# 单例导出
data_fill_engine = DataFillEngine()