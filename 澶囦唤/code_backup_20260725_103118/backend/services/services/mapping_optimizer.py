#!/usr/bin/env python3
"""
映射优化服务 - 增强表名和字段名的映射质量
核心功能：
1. 智能检测无意义映射
2. 提供高质量翻译建议
3. 验证映射质量
4. 保持向后兼容
"""
import json
import os
import re
from typing import Dict, List, Optional, Tuple, Any

from core.field_name_manager import WORD_DICTIONARY

class MappingOptimizer:
    """
    映射优化服务 - 作为现有映射管理的增强层
    不修改原有逻辑，只做增量优化
    """
    
    def __init__(self):
        # 加载现有管理器
        from core.table_name_manager import TableNameManager
        from core.field_name_manager import FieldNameManager
        
        self.table_name_manager = TableNameManager()
        self.field_name_manager = FieldNameManager()
        self.word_dictionary = WORD_DICTIONARY
        
        # 加载优化规则库
        self.rules = self._load_rules()
        
        # 初始化统计
        self.stats = {
            'total_optimizations': 0,
            'fixed_meaninless': 0,
            'improved_translations': 0
        }
    
    def _load_rules(self) -> Dict:
        """加载映射优化规则库"""
        rules_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'mapping_rules.json')
        
        default_rules = {
            # 无意义字段名模式
            'meaningless_patterns': [
                r'^tmp[a-zA-Z0-9_]+$',
                r'^Unnamed:\s*\d+$',
                r'^field_\d+$',
                r'^col_\d+$',
                r'^\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}:\d{2})?$',
                r'^sheet\d+$'
            ],
            
            # 常用表名规则
            'table_name_rules': {
                '教师基础信息': 'teacher_basic_info',
                '教师学历记录': 'teacher_education_record',
                '岗位聘任信息': 'post_appointment_info',
                '绩效工资审批': 'performance_pay_approval',
                '职工退休呈报表': 'retirement_report',
                '单位名称字典': 'unit_dictionary',
                '个人身份字典': 'personal_identity_dictionary',
                '职称字典': 'title_dictionary',
                '岗位名称字典': 'post_name_dictionary',
                '学历层次字典': 'education_level_dictionary',
                '教师职务记录': 'teacher_position_record',
                '教师资格证信息': 'teacher_certificate_info',
                '绩效工资月报表': 'performance_pay_monthly_report',
                '高龄老人补贴信息': 'elderly_subsidy_info',
                '退休补充信息': 'retirement_supplement_info'
            },
            
            # 常用字段名规则（扩展现有词典）
            'field_name_rules': {
                # 补充教育行业专用词汇
                '教师编号': 'teacher_code',
                '教师ID': 'teacher_id',
                '单位代码': 'unit_code',
                '单位名称': 'unit_name',
                '岗位代码': 'post_code',
                '岗位名称': 'post_name',
                '岗位等级': 'post_level',
                '薪级': 'pay_scale',
                '薪级工资': 'scale_salary',
                '岗位工资': 'post_salary',
                '绩效工资': 'performance_pay',
                '应发工资': 'gross_salary',
                '实发工资': 'net_salary',
                '代扣款项': 'deductions',
                '养老保险': 'pension_insurance',
                '医疗保险': 'medical_insurance',
                '失业保险': 'unemployment_insurance',
                '工伤保险': 'work_injury_insurance',
                '生育保险': 'maternity_insurance',
                '住房公积金': 'housing_fund',
                '职业年金': 'occupational_pension',
                '乡镇补贴': 'township_subsidy',
                '生活补贴': 'living_subsidy',
                '交通补贴': 'transport_subsidy',
                '通讯补贴': 'communication_subsidy',
                '住房补贴': 'housing_subsidy',
                '独生子女费': 'only_child_allowance',
                '独生子女证号': 'only_child_cert_no',
                '退休日期': 'retirement_date',
                '退休原因': 'retirement_reason',
                '退休费': 'retirement_fee',
                '退休待遇': 'retirement_treatment',
                '审批状态': 'approval_status',
                '审批日期': 'approval_date',
                '审批人': 'approver',
                '备注信息': 'remarks',
                '数据来源': 'data_source',
                '导入时间': 'import_time',
                '导入批次': 'import_batch'
            },
            
            # 命名规范规则
            'naming_rules': {
                'max_length': 64,
                'valid_chars': r'^[a-z][a-z0-9_]*$',
                'reserved_names': ['id', 'created_at', 'updated_at']
            }
        }
        
        if os.path.exists(rules_file):
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    custom_rules = json.load(f)
                    # 合并规则
                    default_rules.update(custom_rules)
            except Exception as e:
                print(f"加载规则文件失败，使用默认规则: {e}")
        
        return default_rules
    
    def is_meaningless(self, name: str) -> bool:
        """
        判断名称是否无意义
        """
        if not name or not name.strip():
            return True
        
        name = name.strip()
        
        for pattern in self.rules.get('meaningless_patterns', []):
            if re.match(pattern, name, re.IGNORECASE):
                return True
        
        return False
    
    def optimize_table_name(self, chinese_name: str) -> Tuple[str, bool]:
        """
        优化表名映射
        
        Returns:
            (english_name, is_optimized)
        """
        if not chinese_name or not chinese_name.strip():
            return None, False
        
        chinese_name = chinese_name.strip()
        
        # 1. 检查是否已存在有效映射
        existing_english = self.table_name_manager.get_english_name(chinese_name)
        if existing_english:
            # 检查现有映射是否有效
            if not self.is_meaningless(existing_english):
                return existing_english, False
        
        # 2. 检查规则库
        if chinese_name in self.rules.get('table_name_rules', {}):
            return self.rules['table_name_rules'][chinese_name], True
        
        # 3. 使用智能生成（拼音转换）
        pinyin_name = self._generate_pinyin_name(chinese_name)
        return pinyin_name, True
    
    def optimize_field_name(self, chinese_name: str) -> Tuple[str, bool]:
        """
        优化字段名映射
        
        Returns:
            (english_name, is_optimized)
        """
        if not chinese_name or not chinese_name.strip():
            return None, False
        
        chinese_name = chinese_name.strip()
        
        # 1. 检测无意义字段
        if self.is_meaningless(chinese_name):
            return None, False  # 返回None表示需要人工处理
        
        # 2. 检查是否已存在有效映射
        existing_english = self.field_name_manager.get_english_name(chinese_name)
        if existing_english:
            if not self.is_meaningless(existing_english):
                # 验证现有映射质量
                is_valid, msg = self.field_name_manager.validate_translation_quality(chinese_name, existing_english)
                if is_valid:
                    return existing_english, False
        
        # 3. 检查扩展规则库
        if chinese_name in self.rules.get('field_name_rules', {}):
            return self.rules['field_name_rules'][chinese_name], True
        
        # 4. 使用现有字段名管理器的智能翻译
        new_english = self.field_name_manager._smart_translate(chinese_name)
        
        # 5. 验证新生成的名称
        if new_english and not self.is_meaningless(new_english):
            # 保存到字段名管理器
            if chinese_name not in self.field_name_manager.field_mappings.get("mappings", {}):
                self.field_name_manager._generate_english_name(chinese_name)
            return new_english, True
        
        return None, False
    
    def process_field_configs(self, field_configs: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        处理字段配置列表，优化字段名映射
        
        Returns:
            (processed_configs, pending_fields) - 处理后的配置，需要人工处理的字段
        """
        processed_configs = []
        pending_fields = []
        
        for field in field_configs:
            chinese_name = field.get('chinese_name') or field.get('sourceField') or field.get('source_name', '')
            
            if not chinese_name or not chinese_name.strip():
                processed_configs.append(field)
                continue
            
            # 优化字段名
            english_name, is_optimized = self.optimize_field_name(chinese_name)
            
            if english_name:
                field_copy = field.copy()
                field_copy['english_name'] = english_name
                field_copy['targetField'] = english_name
                if is_optimized:
                    field_copy['optimized'] = True
                processed_configs.append(field_copy)
            else:
                # 需要人工处理
                pending_fields.append({
                    'chinese_name': chinese_name,
                    'original_field': field,
                    'reason': '无意义字段或无法自动翻译'
                })
                processed_configs.append(field)
        
        return processed_configs, pending_fields
    
    def validate_mapping_quality(self, chinese_name: str, english_name: str) -> Tuple[bool, str]:
        """
        验证映射质量
        
        Returns:
            (is_valid, message)
        """
        # 1. 检查无意义模式
        if self.is_meaningless(english_name):
            return False, "字段名无意义，请手动配置"
        
        # 2. 检查命名规范
        max_length = self.rules['naming_rules'].get('max_length', 64)
        if len(english_name) > max_length:
            return False, f"字段名过长（超过{max_length}个字符）"
        
        valid_chars_pattern = self.rules['naming_rules'].get('valid_chars', r'^[a-z][a-z0-9_]*$')
        if not re.match(valid_chars_pattern, english_name):
            return False, "字段名不符合命名规范（必须以小写字母开头，只能包含小写字母、数字和下划线）"
        
        # 3. 检查保留名称
        if english_name in self.rules['naming_rules'].get('reserved_names', []):
            return False, f"字段名 '{english_name}' 是保留名称，请使用其他名称"
        
        # 4. 检查是否包含有意义的单词
        words = english_name.split('_')
        meaningful_words = []
        
        # 检查规则库中的字段名
        for word in words:
            if word in self.rules.get('field_name_rules', {}).values():
                meaningful_words.append(word)
            # 检查字段名管理器的词典
            for dict_val in self.word_dictionary.values():
                if word == dict_val or dict_val.startswith(word + '_') or dict_val.endswith('_' + word):
                    meaningful_words.append(word)
                    break
        
        if len(meaningful_words) == 0:
            # 拼音格式也认为是有效的
            if re.match(r'^[a-z_]+$', english_name):
                return True, "字段名有效（拼音格式）"
            else:
                return False, "字段名缺乏有意义的单词，请使用更具描述性的名称"
        
        return True, f"字段名有效（包含 {len(meaningful_words)} 个有意义的单词）"
    
    def get_translation_suggestions(self, chinese_name: str) -> List[Dict]:
        """
        获取翻译建议
        """
        suggestions = []
        
        # 1. 规则库匹配
        if chinese_name in self.rules.get('field_name_rules', {}):
            suggestions.append({
                'english_name': self.rules['field_name_rules'][chinese_name],
                'source': '规则库匹配',
                'confidence': 1.0
            })
        
        # 2. 使用字段名管理器的建议
        field_suggestions = self.field_name_manager.get_translation_suggestions(chinese_name)
        suggestions.extend(field_suggestions)
        
        # 3. 去重
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            key = s['english_name']
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(s)
        
        return unique_suggestions
    
    def _generate_pinyin_name(self, chinese_name: str) -> str:
        """生成拼音名称"""
        try:
            from pypinyin import pinyin, Style
            py_list = pinyin(chinese_name, style=Style.NORMAL)
            pinyin_str = '_'.join([item[0] for item in py_list])
            result = pinyin_str.lower().replace(' ', '_')
            result = re.sub(r'_+', '_', result)
            
            # 检查是否符合命名规范
            if re.match(r'^[a-z][a-z0-9_]*$', result):
                return result
            
            # 添加前缀使其符合规范
            return f"tbl_{result}"
            
        except Exception as e:
            print(f"拼音转换失败: {e}")
            # 使用时间戳作为后备
            import time
            return f"table_{int(time.time())}"
    
    def get_pending_fields_report(self) -> Dict:
        """获取需要人工处理的字段报告"""
        # 检查现有映射中无意义的字段
        pending_fields = []
        
        # 检查表名映射
        for chinese, mapping in self.table_name_manager.get_all_mappings().items():
            english_name = mapping.get('english_name', '')
            if self.is_meaningless(english_name):
                pending_fields.append({
                    'type': 'table',
                    'chinese_name': chinese,
                    'english_name': english_name,
                    'reason': '无意义的表名映射'
                })
        
        # 检查字段名映射
        for chinese, english in self.field_name_manager.field_mappings.get('mappings', {}).items():
            if self.is_meaningless(english):
                pending_fields.append({
                    'type': 'field',
                    'chinese_name': chinese,
                    'english_name': english,
                    'reason': '无意义的字段名映射'
                })
        
        return {
            'total_pending': len(pending_fields),
            'pending_fields': pending_fields
        }

# 全局映射优化器实例
mapping_optimizer = MappingOptimizer()