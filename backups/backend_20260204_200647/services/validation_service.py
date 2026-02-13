from typing import List, Dict, Any, Optional
import re
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


class Level1Validator:
    """Level 1 验证器：数据格式和类型验证"""

    @staticmethod
    def validate(data: Dict[str, Any], field_config: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        field_name = field_config.get('sourceField', '')
        target_field = field_config.get('targetField', '')
        data_type = field_config.get('dataType', 'VARCHAR')
        value = data.get(field_name)

        # 空值检查
        if value is None or str(value).strip() == '':
            if field_config.get('required', False):
                result.add_error(target_field, f"{field_name} 为必填项", 1)
            return result

        str_value = str(value).strip()

        # 根据数据类型验证
        if data_type == 'INTEGER':
            if not Level1Validator._is_integer(str_value):
                result.add_error(target_field, f"{field_name} 必须是整数", 1)

        elif data_type == 'DECIMAL':
            if not Level1Validator._is_decimal(str_value):
                result.add_error(target_field, f"{field_name} 必须是数字", 1)

        elif data_type == 'DATE':
            if not Level1Validator._is_date(str_value):
                result.add_error(target_field, f"{field_name} 日期格式不正确 (YYYY-MM-DD)", 1)

        elif data_type == 'DATETIME':
            if not Level1Validator._is_datetime(str_value):
                result.add_error(target_field, f"{field_name} 日期时间格式不正确", 1)

        elif data_type == 'BOOLEAN':
            if not Level1Validator._is_boolean(str_value):
                result.add_error(target_field, f"{field_name} 必须是布尔值 (是/否/true/false)", 1)

        elif data_type == 'VARCHAR':
            max_length = field_config.get('length', 255)
            if len(str_value) > max_length:
                result.add_error(target_field, f"{field_name} 长度超过限制 ({max_length}字符)", 1)

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
    """Level 2 验证器：业务逻辑和唯一性验证"""

    def __init__(self):
        self.unique_values: Dict[str, set] = {}

    def validate(self, data: Dict[str, Any], field_config: Dict[str, Any], 
                 row_index: int, all_data: List[Dict[str, Any]]) -> ValidationResult:
        result = ValidationResult()
        field_name = field_config.get('sourceField', '')
        target_field = field_config.get('targetField', '')
        value = data.get(field_name)

        if value is None or str(value).strip() == '':
            return result

        str_value = str(value).strip()
        data_type = field_config.get('dataType', 'VARCHAR')

        # 业务逻辑验证
        if target_field == 'age' or '年龄' in field_name:
            result.merge(self._validate_age(str_value, field_name, target_field))

        if target_field == 'id_card' or '身份证' in field_name:
            result.merge(self._validate_id_card(str_value, field_name, target_field))

        if target_field == 'phone' or target_field == 'mobile' or '电话' in field_name or '手机' in field_name:
            result.merge(self._validate_phone(str_value, field_name, target_field))

        if target_field == 'email' or '邮箱' in field_name:
            result.merge(self._validate_email(str_value, field_name, target_field))

        if '日期' in field_name or '时间' in field_name or target_field.endswith('_date'):
            result.merge(self._validate_date_not_future(str_value, field_name, target_field))

        # 唯一性验证
        if field_config.get('unique', False):
            result.merge(self._validate_unique(str_value, target_field, field_name))

        return result

    def _validate_age(self, value: str, field_name: str, target_field: str) -> ValidationResult:
        result = ValidationResult()
        try:
            age = int(value)
            if age < 0 or age > 150:
                result.add_error(target_field, f"{field_name} 必须在 0-150 之间", 2)
            elif age < 18:
                result.add_warning(target_field, f"{field_name} 小于18岁，请确认", 2)
        except ValueError:
            pass
        return result

    def _validate_id_card(self, value: str, field_name: str, target_field: str) -> ValidationResult:
        result = ValidationResult()
        # 简单验证：15位或18位
        if len(value) not in [15, 18]:
            result.add_error(target_field, f"{field_name} 长度必须为15或18位", 2)
        elif len(value) == 18:
            # 验证最后一位校验码
            if not self._check_id_card_checksum(value):
                result.add_error(target_field, f"{field_name} 校验码不正确", 2)
        return result

    def _check_id_card_checksum(self, id_card: str) -> bool:
        """验证身份证校验码"""
        if len(id_card) != 18:
            return False
        
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        try:
            sum_value = sum(int(id_card[i]) * weights[i] for i in range(17))
            return id_card[17].upper() == check_codes[sum_value % 11]
        except:
            return False

    def _validate_phone(self, value: str, field_name: str, target_field: str) -> ValidationResult:
        result = ValidationResult()
        # 手机号：11位数字，以1开头
        if len(value) == 11 and value.startswith('1'):
            if not value.isdigit():
                result.add_error(target_field, f"{field_name} 格式不正确", 2)
        # 固定电话：区号+号码
        elif not re.match(r'^\d{3,4}-?\d{7,8}$', value):
            result.add_warning(target_field, f"{field_name} 格式可能不正确", 2)
        return result

    def _validate_email(self, value: str, field_name: str, target_field: str) -> ValidationResult:
        result = ValidationResult()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            result.add_error(target_field, f"{field_name} 邮箱格式不正确", 2)
        return result

    def _validate_date_not_future(self, value: str, field_name: str, target_field: str) -> ValidationResult:
        result = ValidationResult()
        try:
            # 尝试解析日期
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日']:
                try:
                    date_obj = datetime.strptime(value, fmt)
                    if date_obj > datetime.now():
                        result.add_error(target_field, f"{field_name} 不能晚于今天", 2)
                    return result
                except ValueError:
                    continue
        except:
            pass
        return result

    def _validate_unique(self, value: str, target_field: str, field_name: str) -> ValidationResult:
        result = ValidationResult()
        if target_field not in self.unique_values:
            self.unique_values[target_field] = set()
        
        if value in self.unique_values[target_field]:
            result.add_error(target_field, f"{field_name} 值 '{value}' 重复", 2)
        else:
            self.unique_values[target_field].add(value)
        
        return result


class Level3Validator:
    """Level 3 验证器：关联数据完整性验证"""

    def __init__(self, reference_data: Optional[Dict[str, List[str]]] = None):
        """
        初始化验证器
        :param reference_data: 参考数据，如 {'department': ['部门1', '部门2', ...]}
        """
        self.reference_data = reference_data or {}

    def validate(self, data: Dict[str, Any], field_config: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        field_name = field_config.get('sourceField', '')
        target_field = field_config.get('targetField', '')
        value = data.get(field_name)

        if value is None or str(value).strip() == '':
            return result

        str_value = str(value).strip()

        # 部门关联验证
        if target_field == 'department' or '部门' in field_name:
            result.merge(self._validate_reference(
                str_value, 'department', field_name, target_field
            ))

        # 学历关联验证
        if target_field == 'education' or '学历' in field_name:
            valid_educations = ['小学', '初中', '高中', '中专', '大专', '本科', '硕士', '博士']
            if str_value not in valid_educations:
                result.add_warning(target_field, f"{field_name} '{str_value}' 不是标准学历", 3)

        # 政治面貌关联验证
        if target_field == 'political_status' or '政治面貌' in field_name:
            valid_status = ['中共党员', '中共预备党员', '共青团员', '民革党员', '民盟盟员', 
                          '民建会员', '民进会员', '农工党党员', '致公党党员', '九三学社社员',
                          '台盟盟员', '无党派人士', '群众']
            if str_value not in valid_status:
                result.add_warning(target_field, f"{field_name} '{str_value}' 不是标准政治面貌", 3)

        # 性别关联验证
        if target_field == 'gender' or '性别' in field_name:
            valid_genders = ['男', '女']
            if str_value not in valid_genders:
                result.add_error(target_field, f"{field_name} 必须是 '男' 或 '女'", 3)

        return result

    def _validate_reference(self, value: str, ref_key: str, 
                           field_name: str, target_field: str) -> ValidationResult:
        result = ValidationResult()
        if ref_key in self.reference_data:
            if value not in self.reference_data[ref_key]:
                result.add_error(target_field, 
                    f"{field_name} '{value}' 在系统中不存在", 3)
        return result


class Level4Validator:
    """Level 4 验证器：外键完整性验证"""

    def __init__(self, parent_data: Optional[Dict[str, Any]] = None):
        """
        初始化验证器
        :param parent_data: 父表数据，用于验证外键关联
        """
        self.parent_data = parent_data or {}

    def validate(self, data: Dict[str, Any], field_config: Dict[str, Any], 
                 table_type: str = "master") -> ValidationResult:
        """
        验证外键完整性
        :param data: 要验证的数据行
        :param field_config: 字段配置
        :param table_type: 表类型
        :return: 验证结果
        """
        result = ValidationResult()
        
        # 只对子表进行外键验证
        if table_type != "child":
            return result
        
        field_name = field_config.get('sourceField', '')
        target_field = field_config.get('targetField', '')
        value = data.get(field_name)
        
        if value is None or str(value).strip() == '':
            return result
        
        str_value = str(value).strip()
        
        # 验证业务主键是否存在于父表中
        if self._is_business_key_field(field_name, target_field):
            if not self._validate_parent_exists(str_value):
                result.add_error(
                    target_field, 
                    f"{field_name} '{str_value}' 在主表中不存在，无法建立关联", 
                    4
                )
        
        return result
    
    def _is_business_key_field(self, field_name: str, target_field: str) -> bool:
        """判断是否为业务主键字段"""
        business_key_patterns = [
            '身份证', 'id_card', '编号', 'code', '工号', '学号', 'no'
        ]
        return any(pattern in field_name or pattern in target_field 
                  for pattern in business_key_patterns)
    
    def _validate_parent_exists(self, business_key: str) -> bool:
        """验证业务主键是否存在于父表中"""
        if not self.parent_data:
            return True  # 如果没有父表数据，跳过验证
        
        # 检查业务主键是否在父表中
        parent_keys = self.parent_data.get('business_keys', set())
        return business_key in parent_keys


class ValidationService:
    """验证服务"""

    def __init__(self):
        self.level2_validator = Level2Validator()
        self.level3_validator = Level3Validator()
        self.level4_validator = Level4Validator()

    def validate_data(self, data: List[Dict[str, Any]], 
                     field_configs: List[Dict[str, Any]],
                     validation_level: int = 4,
                     reference_data: Optional[Dict[str, List[str]]] = None,
                     table_type: str = "master",
                     parent_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        验证数据
        :param data: 要验证的数据列表
        :param field_configs: 字段配置列表
        :param validation_level: 验证级别 (1, 2, 3, 4)
        :param reference_data: 参考数据
        :param table_type: 表类型 (master/child/dictionary)
        :param parent_data: 父表数据（用于Level 4验证）
        :return: 验证报告
        """
        # 重置验证器状态
        self.level2_validator = Level2Validator()
        if validation_level >= 3:
            self.level3_validator = Level3Validator(reference_data)
        if validation_level >= 4:
            self.level4_validator = Level4Validator(parent_data)

        validated_data = []
        total_errors = 0
        total_warnings = 0

        for row_index, row in enumerate(data):
            row_result = {
                'row_index': row_index,
                'data': row,
                'errors': [],
                'warnings': [],
                'is_valid': True
            }

            for field_config in field_configs:
                # Level 1 验证
                level1_result = Level1Validator.validate(row, field_config)
                if not level1_result.is_valid:
                    for error in level1_result.errors:
                        row_result['errors'].append({
                            'field': error.field,
                            'message': error.message,
                            'level': error.level
                        })
                        total_errors += 1

                # Level 2 验证
                if validation_level >= 2:
                    level2_result = self.level2_validator.validate(
                        row, field_config, row_index, data
                    )
                    if not level2_result.is_valid:
                        for error in level2_result.errors:
                            row_result['errors'].append({
                                'field': error.field,
                                'message': error.message,
                                'level': error.level
                            })
                            total_errors += 1
                    for warning in level2_result.warnings:
                        row_result['warnings'].append({
                            'field': warning.field,
                            'message': warning.message,
                            'level': warning.level
                        })
                        total_warnings += 1

                # Level 3 验证
                if validation_level >= 3:
                    level3_result = self.level3_validator.validate(row, field_config)
                    if not level3_result.is_valid:
                        for error in level3_result.errors:
                            row_result['errors'].append({
                                'field': error.field,
                                'message': error.message,
                                'level': error.level
                            })
                            total_errors += 1
                    for warning in level3_result.warnings:
                        row_result['warnings'].append({
                            'field': warning.field,
                            'message': warning.message,
                            'level': warning.level
                        })
                        total_warnings += 1

                # Level 4 验证（外键完整性）
                if validation_level >= 4:
                    level4_result = self.level4_validator.validate(
                        row, field_config, table_type
                    )
                    if not level4_result.is_valid:
                        for error in level4_result.errors:
                            row_result['errors'].append({
                                'field': error.field,
                                'message': error.message,
                                'level': error.level
                            })
                            total_errors += 1

            # 标记行是否有效
            row_result['is_valid'] = len(row_result['errors']) == 0
            validated_data.append(row_result)

        # 生成验证报告
        valid_count = sum(1 for r in validated_data if r['is_valid'])
        invalid_count = len(validated_data) - valid_count

        return {
            'summary': {
                'total_rows': len(data),
                'valid_rows': valid_count,
                'invalid_rows': invalid_count,
                'total_errors': total_errors,
                'total_warnings': total_warnings,
                'validation_level': validation_level,
                'table_type': table_type
            },
            'validated_data': validated_data
        }
