"""
数据处理模块
使用Pandas进行数据查询、转换和计算
"""
import pandas as pd
import psycopg2
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Union
import re

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


class DataProcessor:
    """数据处理器 - 使用Pandas进行数据处理"""
    
    def __init__(self):
        self.conn = None
        self.transform_functions = {
            'calculate_age': self.calculate_age,
            'format_date': self.format_date,
            'format_date_cn': self.format_date_cn,
            'convert_gender': self.convert_gender,
            'format_money': self.format_money,
            'upper': lambda x: str(x).upper() if x else '',
            'lower': lambda x: str(x).lower() if x else '',
            'strip': lambda x: str(x).strip() if x else '',
        }
    
    def connect(self) -> bool:
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(**DATABASE_CONFIG)
            print("[数据处理器] 数据库连接成功")
            return True
        except Exception as e:
            print(f"[数据处理器] 数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            print("[数据处理器] 数据库连接已关闭")
    
    def query_data(self, sql: str) -> pd.DataFrame:
        """
        查询数据
        
        Args:
            sql: SQL查询语句
        
        Returns:
            Pandas DataFrame
        """
        if not self.conn:
            self.connect()
        
        try:
            df = pd.read_sql(sql, self.conn)
            print(f"[数据查询] 成功，返回 {len(df)} 条记录")
            return df
        except Exception as e:
            print(f"[数据查询] 失败: {e}")
            return pd.DataFrame()
    
    def query_by_config(self, config: Dict[str, Any]) -> pd.DataFrame:
        """
        根据配置查询数据
        
        Args:
            config: 数据源配置
                {
                    'primary': 'teacher_basic_info',
                    'related': [
                        {
                            'table': 'retirement_info',
                            'join_field': 'id_card',
                            'join_type': 'LEFT'
                        }
                    ],
                    'filters': [
                        {
                            'field': 'employment_status',
                            'operator': '=',
                            'value': '退休'
                        }
                    ]
                }
        
        Returns:
            Pandas DataFrame
        """
        primary_table = config.get('primary')
        if not primary_table:
            raise ValueError("缺少主表配置")
        
        sql = f"SELECT * FROM {primary_table}"
        
        related_tables = config.get('related', [])
        if related_tables:
            for i, related in enumerate(related_tables):
                table = related['table']
                join_field = related['join_field']
                join_type = related.get('join_type', 'LEFT')
                alias = f"t{i+1}"
                
                sql = sql.replace(f"FROM {primary_table}", 
                                f"FROM {primary_table} t0")
                sql = f"{sql} {join_type} JOIN {table} {alias} ON t0.{join_field} = {alias}.{join_field}"
        
        filters = config.get('filters', [])
        if filters:
            where_clauses = []
            for filter_item in filters:
                field = filter_item['field']
                operator = filter_item['operator']
                value = filter_item['value']
                
                if isinstance(value, str):
                    where_clauses.append(f"{field} {operator} '{value}'")
                else:
                    where_clauses.append(f"{field} {operator} {value}")
            
            sql = f"{sql} WHERE {' AND '.join(where_clauses)}"
        
        return self.query_data(sql)
    
    def transform_field(self, value: Any, transform_name: str, **kwargs) -> Any:
        """
        转换字段值
        
        Args:
            value: 原始值
            transform_name: 转换函数名称
            **kwargs: 转换函数参数
        
        Returns:
            转换后的值
        """
        if transform_name not in self.transform_functions:
            print(f"[数据转换] 未知的转换函数: {transform_name}")
            return value
        
        try:
            func = self.transform_functions[transform_name]
            return func(value, **kwargs)
        except Exception as e:
            print(f"[数据转换] 转换失败: {e}")
            return value
    
    def transform_dataframe(self, df: pd.DataFrame, field_mappings: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        转换DataFrame
        
        Args:
            df: 原始DataFrame
            field_mappings: 字段映射配置
                [
                    {
                        'source_field': 'birth_date',
                        'target_field': 'age',
                        'transform': 'calculate_age'
                    }
                ]
        
        Returns:
            转换后的DataFrame
        """
        result_df = df.copy()
        
        for mapping in field_mappings:
            source_field = mapping.get('source_field')
            target_field = mapping.get('target_field', source_field)
            transform = mapping.get('transform')
            
            if source_field not in result_df.columns:
                print(f"[数据转换] 源字段不存在: {source_field}")
                continue
            
            if transform:
                result_df[target_field] = result_df[source_field].apply(
                    lambda x: self.transform_field(x, transform)
                )
                print(f"[数据转换] {source_field} -> {target_field} ({transform})")
            else:
                if target_field != source_field:
                    result_df[target_field] = result_df[source_field]
        
        return result_df
    
    def calculate_statistics(self, df: pd.DataFrame, calc_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算统计值
        
        Args:
            df: DataFrame
            calc_config: 统计配置
                [
                    {
                        'name': '退休人数',
                        'type': 'count'
                    },
                    {
                        'name': '平均年龄',
                        'type': 'mean',
                        'field': 'age'
                    }
                ]
        
        Returns:
            统计结果字典
        """
        results = {}
        
        for calc in calc_config:
            name = calc['name']
            calc_type = calc['type']
            field = calc.get('field')
            
            if calc_type == 'count':
                results[name] = len(df)
            elif calc_type == 'sum' and field:
                results[name] = df[field].sum()
            elif calc_type == 'mean' and field:
                results[name] = df[field].mean()
            elif calc_type == 'max' and field:
                results[name] = df[field].max()
            elif calc_type == 'min' and field:
                results[name] = df[field].min()
            else:
                print(f"[统计计算] 未知的统计类型: {calc_type}")
        
        print(f"[统计计算] 结果: {results}")
        return results
    
    @staticmethod
    def calculate_age(birth_date: Union[str, date, datetime], reference_date: Optional[date] = None) -> int:
        """
        计算年龄
        
        Args:
            birth_date: 出生日期
            reference_date: 参考日期（默认为今天）
        
        Returns:
            年龄
        """
        if pd.isna(birth_date):
            return 0
        
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        elif isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        
        if reference_date is None:
            reference_date = date.today()
        
        age = reference_date.year - birth_date.year
        if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return age
    
    @staticmethod
    def format_date(date_value: Union[str, date, datetime], fmt: str = '%Y-%m-%d') -> str:
        """
        格式化日期
        
        Args:
            date_value: 日期值
            fmt: 格式字符串
        
        Returns:
            格式化后的日期字符串
        """
        if pd.isna(date_value):
            return ''
        
        if isinstance(date_value, str):
            date_value = datetime.strptime(date_value, '%Y-%m-%d')
        elif isinstance(date_value, date):
            date_value = datetime.combine(date_value, datetime.min.time())
        
        return date_value.strftime(fmt)
    
    @staticmethod
    def format_date_cn(date_value: Union[str, date, datetime]) -> str:
        """
        格式化日期为中文格式
        
        Args:
            date_value: 日期值
        
        Returns:
            中文格式日期字符串（如：2024年5月10日）
        """
        if pd.isna(date_value):
            return ''
        
        if isinstance(date_value, str):
            date_value = datetime.strptime(date_value, '%Y-%m-%d')
        elif isinstance(date_value, date):
            date_value = datetime.combine(date_value, datetime.min.time())
        
        return f"{date_value.year}年{date_value.month}月{date_value.day}日"
    
    @staticmethod
    def convert_gender(gender_code: Union[str, int]) -> str:
        """
        转换性别代码为中文
        
        Args:
            gender_code: 性别代码（'1'/'2' 或 '男'/'女'）
        
        Returns:
            性别中文（'男'/'女'）
        """
        if pd.isna(gender_code):
            return ''
        
        gender_str = str(gender_code)
        
        if gender_str in ['1', '男', 'M', 'm']:
            return '男'
        elif gender_str in ['2', '女', 'F', 'f']:
            return '女'
        else:
            return gender_str
    
    @staticmethod
    def format_money(amount: Union[int, float], decimal_places: int = 2) -> str:
        """
        格式化金额
        
        Args:
            amount: 金额
            decimal_places: 小数位数
        
        Returns:
            格式化后的金额字符串
        """
        if pd.isna(amount):
            return '0.00元'
        
        return f"{amount:,.{decimal_places}f}元"
    
    def register_transform_function(self, name: str, func: callable):
        """
        注册自定义转换函数
        
        Args:
            name: 函数名称
            func: 函数对象
        """
        self.transform_functions[name] = func
        print(f"[数据处理器] 注册转换函数: {name}")


if __name__ == '__main__':
    print("\n=== 数据处理器测试 ===\n")
    
    processor = DataProcessor()
    
    print("测试年龄计算:")
    birth_date = "1965-06-07"
    age = processor.calculate_age(birth_date)
    print(f"  出生日期: {birth_date}, 年龄: {age}")
    
    print("\n测试日期格式化:")
    test_date = "2024-05-10"
    print(f"  标准格式: {processor.format_date(test_date)}")
    print(f"  中文格式: {processor.format_date_cn(test_date)}")
    
    print("\n测试性别转换:")
    print(f"  1 -> {processor.convert_gender('1')}")
    print(f"  2 -> {processor.convert_gender('2')}")
    
    print("\n测试金额格式化:")
    print(f"  1234567.89 -> {processor.format_money(1234567.89)}")
    
    print("\n测试完成!")
