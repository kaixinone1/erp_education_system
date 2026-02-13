#!/usr/bin/env python3
"""
通用验证服务 - 100% 配置驱动

所有验证规则从 merged_schema_mappings.json 读取
不硬编码任何表名、字段名或验证逻辑
"""

import json
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime


class ValidationError:
    """验证错误信息"""
    def __init__(self, field: str, message: str, level: int):
        self.field = field
        self.message = message
        self.level = level


class ValidationResult:
    """验证结果"""
    def __init__(self):
        self.is_valid = True
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def add_error(self, field: str, message: str, level: int = 1):
        self.errors.append(ValidationError(field, message, level))
        self.is_valid = False

    def add_warning(self, field: str, message: str, level: int = 1):
        self.warnings.append(ValidationError(field, message, level))

    def merge(self, other: 'ValidationResult'):
        """合并另一个验证结果"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False


class ConfigLoader:
    """配置加载器 - 从 merged_schema_mappings.json 读取配置"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config', 'merged_schema_mappings.json'
        )
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            self._config = {"tables": {}, "mappings": {}, "validation_rules": {}}
    
    def get_table_config(self, table_name: str) -> Dict:
        """获取表配置"""
        return self._config.get("tables", {}).get(table_name, {})
    
    def get_field_config(self, table_name: str, field_name: str) -> Dict:
        """获取字段配置"""
        table_config = self.get_table_config(table_name)
        fields = table_config.get("fields", [])
        for field in fields:
            if field.get("name") == field_name or field.get("chinese_name") == field_name:
                return field
        return {}
    
    def get_mapping_config(self, field_name: str) -> Dict:
        """获取字段映射配置"""
        return self._config.get("mappings", {}).get(field_name, {})
    
    def get_validation_rules(self) -> Dict:
        """获取验证规则"""
        return self._config.get("validation_rules", {})
    
    def get_dictionary_values(self, dict_name: str) -> List[str]:
        """获取字典值列表"""
        return self._config.get("validation_rules", {}).get("dictionaries", {}).get(dict_name, [])
    
    def reload(self):
        """重新加载配置"""
        self._load_config()


# 全局配置加载器
config_loader = ConfigLoader()


class Level1Validator:
    """
    Level 1 验证器：数据格式和类型验证
    
    验证规则来源：
    - 数据类型：从 field_config.data_type 读取
    - 必填：从 field_config.required 读取
    - 长度：从 field_config.length 读取
    """

    @staticmethod
    def validate(data: Dict[str, Any], field_config: Dict[str, Any], 
                 table_name: str = "") -> ValidationResult:
        """
        验证单个字段
        
        Args:
            data: 数据行
            field_config: 字段配置（从前端传入或从配置文件读取）
            table_name: 表名（用于从配置文件读取额外规则）
        """
        result = ValidationResult()
        
        # 获取字段名
        source_field = field_config.get('sourceField') or field_config.get('chinese_name', '')
        target_field = field_config.get('targetField') or field_config.get('name', '')
        
        # 获取数据类型
        data_type = field_config.get('dataType') or field_config.get('data_type', 'VARCHAR')
        
        # 获取值
        value = data.get(source_field)
        
        # 从配置文件读取额外规则
        if table_name:
            config_field = config_loader.get_field_config(table_name, target_field)
            if config_field:
                # 合并配置
                field_config = {**config_field, **field_config}
        
        # 空值检查 - 从配置读取 required
        required = field_config.get('required', False) or field_config.get('not_null', False)
        if value is None or str(value).strip() == '':
            if required:
                result.add_error(target_field, f"{source_field} 为必填项", 1)
            return result
        
        str_value = str(value).strip()
        
        # 根据数据类型验证
        if data_type == 'INTEGER':
            if not Level1Validator._is_integer(str_value):
                result.add_error(target_field, f"{source_field} 必须是整数", 1)
        
        elif data_type == 'DECIMAL' or data_type == 'NUMERIC':
            if not Level1Validator._is_decimal(str_value):
                result.add_error(target_field, f"{source_field} 必须是数字", 1)
        
        elif data_type == 'DATE':
            if not Level1Validator._is_date(str_value):
                result.add_error(target_field, f"{source_field} 日期格式不正确", 1)
        
        elif data_type == 'DATETIME':
            if not Level1Validator._is_datetime(str_value):
                result.add_error(target_field, f"{source_field} 日期时间格式不正确", 1)
        
        elif data_type == 'BOOLEAN':
            if not Level1Validator._is_boolean(str_value):
                result.add_error(target_field, f"{source_field} 必须是布尔值", 1)
        
        elif data_type == 'VARCHAR':
            # 从配置读取长度
            max_length = field_config.get('length', 255)
            if len(str_value) > max_length:
                result.add_error(target_field, f"{source_field} 长度超过限制 ({max_length}字符)", 1)
        
        return result
    
    @staticmethod
    def _is_integer(value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _is_decimal(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _is_date(value: str) -> bool:
        patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{4}/\d{2}/\d{2}$',
            r'^\d{4}年\d{2}月\d{2}日$'
        ]
        for pattern in patterns:
            if re.match(pattern, value):
                return True
        return False
    
    @staticmethod
    def _is_datetime(value: str) -> bool:
        patterns = [
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$'
        ]
        for pattern in patterns:
            if re.match(pattern, value):
                return True
        return False
    
    @staticmethod
    def _is_boolean(value: str) -> bool:
        return value.lower() in ['true', 'false', '是', '否', '1', '0', 'yes', 'no']


class Level2Validator:
    """
    Level 2 验证器：业务逻辑验证
    
    验证规则来源：
    - 从 merged_schema_mappings.json 的 validation_rules 读取
    - 支持：regex、range、unique 等规则
    """

    def __init__(self):
        self.unique_values: Dict[str, set] = {}
        self.validation_rules = config_loader.get_validation_rules()
    
    def validate(self, data: Dict[str, Any], field_config: Dict[str, Any],
                 table_name: str = "", row_index: int = 0) -> ValidationResult:
        """
        验证业务逻辑
        
        Args:
            data: 数据行
            field_config: 字段配置
            table_name: 表名
            row_index: 行索引
        """
        result = ValidationResult()
        
        source_field = field_config.get('sourceField') or field_config.get('chinese_name', '')
        target_field = field_config.get('targetField') or field_config.get('name', '')
        value = data.get(source_field)
        
        if value is None or str(value).strip() == '':
            return result
        
        str_value = str(value).strip()
        
        # 从字段配置读取验证规则
        validation = field_config.get('validation', {})
        
        # 1. 正则表达式验证
        if 'regex' in validation:
            pattern = validation['regex']
            if not re.match(pattern, str_value):
                result.add_error(target_field, f"{source_field} 格式不正确", 2)
        
        # 2. 范围验证
        if 'range' in validation:
            range_config = validation['range']
            result.merge(self._validate_range(str_value, range_config, source_field, target_field))
        
        # 3. 唯一性验证
        if field_config.get('unique', False):
            result.merge(self._validate_unique(str_value, target_field, source_field))
        
        # 4. 从 common rules 查找匹配的规则
        for rule_name, rule_config in self.validation_rules.get('common', {}).items():
            # 检查字段名是否匹配规则名（如 age 字段匹配 age 规则）
            if target_field == rule_name or rule_name in target_field.lower():
                if rule_config.get('type') == 'regex':
                    if not re.match(rule_config['pattern'], str_value):
                        result.add_error(target_field, f"{source_field} {rule_config.get('description', '格式不正确')}", 2)
                elif rule_config.get('type') == 'range':
                    result.merge(self._validate_range(str_value, rule_config, source_field, target_field))
        
        return result
    
    def _validate_range(self, value: str, range_config: Dict, 
                       field_name: str, target_field: str) -> ValidationResult:
        """验证范围"""
        result = ValidationResult()
        try:
            num_value = float(value)
            min_val = range_config.get('min')
            max_val = range_config.get('max')
            warning_min = range_config.get('warning_min')
            
            if min_val is not None and num_value < min_val:
                result.add_error(target_field, f"{field_name} 必须大于等于 {min_val}", 2)
            
            if max_val is not None and num_value > max_val:
                result.add_error(target_field, f"{field_name} 必须小于等于 {max_val}", 2)
            
            if warning_min is not None and num_value < warning_min:
                result.add_warning(target_field, f"{field_name} 小于 {warning_min}，请确认", 2)
                
        except ValueError:
            pass
        return result
    
    def _validate_unique(self, value: str, target_field: str, field_name: str) -> ValidationResult:
        """验证唯一性"""
        result = ValidationResult()
        if target_field not in self.unique_values:
            self.unique_values[target_field] = set()
        
        if value in self.unique_values[target_field]:
            result.add_error(target_field, f"{field_name} 值 '{value}' 重复", 2)
        else:
            self.unique_values[target_field].add(value)
        
        return result


class Level3Validator:
    """
    Level 3 验证器：关联数据完整性验证
    
    验证规则来源：
    - 从 field_config.relation 读取关联配置
    - 从 validation_rules.dictionaries 读取字典值
    """

    def __init__(self, reference_data: Optional[Dict[str, List[str]]] = None):
        """
        初始化验证器
        :param reference_data: 参考数据，如 {'department': ['部门1', '部门2', ...]}
        """
        self.reference_data = reference_data or {}
        self.validation_rules = config_loader.get_validation_rules()
    
    def validate(self, data: Dict[str, Any], field_config: Dict[str, Any],
                 table_name: str = "") -> ValidationResult:
        """
        验证关联数据完整性
        
        Args:
            data: 数据行
            field_config: 字段配置
            table_name: 表名
        """
        result = ValidationResult()
        
        source_field = field_config.get('sourceField') or field_config.get('chinese_name', '')
        target_field = field_config.get('targetField') or field_config.get('name', '')
        value = data.get(source_field)
        
        if value is None or str(value).strip() == '':
            return result
        
        str_value = str(value).strip()
        
        # 1. 从 relation 配置读取关联规则
        relation = field_config.get('relation', {})
        if relation:
            relation_type = relation.get('type')
            
            if relation_type == 'dictionary':
                # 字典关联验证
                dict_name = relation.get('dictionary_name', target_field)
                valid_values = config_loader.get_dictionary_values(dict_name)
                if valid_values and str_value not in valid_values:
                    result.add_warning(target_field, 
                        f"{source_field} '{str_value}' 不在标准字典值中", 3)
            
            elif relation_type == 'foreign_key':
                # 外键关联验证
                ref_table = relation.get('ref_table')
                ref_field = relation.get('ref_field')
                if ref_table and ref_field:
                    result.merge(self._validate_foreign_key(
                        str_value, ref_table, ref_field, source_field, target_field
                    ))
        
        # 2. 从 target_field 推断字典类型
        for dict_name in self.validation_rules.get('dictionaries', {}).keys():
            if target_field == dict_name or dict_name in target_field.lower():
                valid_values = config_loader.get_dictionary_values(dict_name)
                if valid_values and str_value not in valid_values:
                    result.add_warning(target_field, 
                        f"{source_field} '{str_value}' 不是标准值", 3)
        
        # 3. 从 reference_data 验证
        for ref_key, ref_values in self.reference_data.items():
            if target_field == ref_key or ref_key in target_field.lower():
                if str_value not in ref_values:
                    result.add_error(target_field, 
                        f"{source_field} '{str_value}' 在系统中不存在", 3)
        
        return result
    
    def _validate_foreign_key(self, value: str, ref_table: str, ref_field: str,
                             field_name: str, target_field: str) -> ValidationResult:
        """验证外键关联"""
        result = ValidationResult()
        # 这里应该查询数据库验证外键是否存在
        # 暂时使用 reference_data 验证
        ref_key = f"{ref_table}.{ref_field}"
        if ref_key in self.reference_data:
            if value not in self.reference_data[ref_key]:
                result.add_error(target_field, 
                    f"{field_name} '{value}' 在关联表 {ref_table} 中不存在", 3)
        return result


class Level4Validator:
    """
    Level 4 验证器：跨表外键完整性验证
    
    验证规则来源：
    - 从 field_config.relation 读取外键配置
    - 查询数据库验证外键存在性
    """

    def __init__(self, db_connection=None):
        """
        初始化验证器
        :param db_connection: 数据库连接
        """
        self.db_connection = db_connection
    
    def validate(self, data: Dict[str, Any], field_config: Dict[str, Any],
                 table_name: str = "", table_type: str = "master") -> ValidationResult:
        """
        验证外键完整性
        
        Args:
            data: 数据行
            field_config: 字段配置
            table_name: 表名
            table_type: 表类型（master/child/dictionary）
        """
        result = ValidationResult()
        
        # 只对子表进行外键验证
        if table_type != "child":
            return result
        
        source_field = field_config.get('sourceField') or field_config.get('chinese_name', '')
        target_field = field_config.get('targetField') or field_config.get('name', '')
        value = data.get(source_field)
        
        if value is None or str(value).strip() == '':
            return result
        
        str_value = str(value).strip()
        
        # 从 relation 配置读取外键规则
        relation = field_config.get('relation', {})
        if relation and relation.get('type') == 'foreign_key':
            ref_table = relation.get('ref_table')
            ref_field = relation.get('ref_field')
            
            if ref_table and ref_field and self.db_connection:
                # 查询数据库验证外键存在性
                if not self._check_foreign_key_exists(ref_table, ref_field, str_value):
                    result.add_error(target_field, 
                        f"{source_field} '{str_value}' 在父表 {ref_table} 中不存在", 4)
        
        return result
    
    def _check_foreign_key_exists(self, ref_table: str, ref_field: str, value: str) -> bool:
        """检查外键值是否存在于父表"""
        if not self.db_connection:
            return True  # 没有数据库连接，默认通过
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                f"SELECT 1 FROM {ref_table} WHERE {ref_field} = %s LIMIT 1",
                (value,)
            )
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        except Exception as e:
            print(f"外键验证失败: {e}")
            return True  # 验证失败，默认通过


class ValidationService:
    """
    验证服务 - 整合所有验证器
    """
    
    def __init__(self, db_connection=None):
        self.level1 = Level1Validator()
        self.level2 = Level2Validator()
        self.level3 = Level3Validator()
        self.level4 = Level4Validator(db_connection)
    
    def validate_row(self, data: Dict[str, Any], field_configs: List[Dict],
                     table_name: str = "", table_type: str = "master",
                     row_index: int = 0) -> ValidationResult:
        """
        验证单行数据
        
        Args:
            data: 数据行
            field_configs: 字段配置列表
            table_name: 表名
            table_type: 表类型
            row_index: 行索引
        """
        result = ValidationResult()
        
        for field_config in field_configs:
            # Level 1: 数据格式验证
            result.merge(self.level1.validate(data, field_config, table_name))
            
            # Level 2: 业务逻辑验证
            result.merge(self.level2.validate(data, field_config, table_name, row_index))
            
            # Level 3: 关联数据验证
            result.merge(self.level3.validate(data, field_config, table_name))
            
            # Level 4: 外键完整性验证
            result.merge(self.level4.validate(data, field_config, table_name, table_type))
        
        return result
    
    def validate_all(self, data_list: List[Dict], field_configs: List[Dict],
                     table_name: str = "", table_type: str = "master") -> List[ValidationResult]:
        """
        验证所有数据
        
        Args:
            data_list: 数据列表
            field_configs: 字段配置列表
            table_name: 表名
            table_type: 表类型
        """
        results = []
        for i, data in enumerate(data_list):
            result = self.validate_row(data, field_configs, table_name, table_type, i)
            results.append(result)
        return results
    
    def validate_data(self, data: List[Dict], field_configs: List[Dict],
                      validation_level: int = 3, reference_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        验证数据（兼容旧接口）
        
        Args:
            data: 数据列表
            field_configs: 字段配置列表
            validation_level: 验证级别（1-4）
            reference_data: 参考数据
        
        Returns:
            验证结果（包含 validated_data 和 summary，兼容前端期望格式）
        """
        # 更新参考数据
        if reference_data:
            self.level3.reference_data = reference_data
        
        # 执行验证
        results = self.validate_all(data, field_configs)
        
        # 构建验证后的数据（包含错误标记）
        validated_data = []
        total_errors = 0
        total_warnings = 0
        invalid_rows = 0
        
        for i, (row, result) in enumerate(zip(data, results)):
            # 使用前端期望的格式
            validated_row = {
                'row_index': i,
                'data': dict(row),
                'is_valid': result.is_valid,
                'errors': [],
                'warnings': []
            }
            
            # 添加错误和警告（使用前端期望的格式）
            if result.errors:
                for error in result.errors:
                    validated_row['errors'].append({
                        'field': error.field,
                        'message': error.message,
                        'level': error.level
                    })
                total_errors += len(result.errors)
                invalid_rows += 1
            
            if result.warnings:
                for warning in result.warnings:
                    validated_row['warnings'].append({
                        'field': warning.field,
                        'message': warning.message,
                        'level': warning.level
                    })
                total_warnings += len(result.warnings)
            
            validated_data.append(validated_row)
        
        # 构建汇总信息
        summary = {
            "total_rows": len(data),
            "valid_rows": len(data) - invalid_rows,
            "invalid_rows": invalid_rows,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "validation_level": validation_level
        }
        
        return {
            "is_valid": invalid_rows == 0,
            "validated_data": validated_data,
            "summary": summary,
            "errors": [],
            "warnings": []
        }
