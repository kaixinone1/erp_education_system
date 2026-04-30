#!/usr/bin/env python3
"""
字段名管理模块
管理中文字段名到英文字段名的唯一映射
使用本地词典 + 智能分词组合生成有意义的英文字段名
完全离线，无需API
"""
import json
import os
import re
from typing import Dict, Optional

# 字段名映射文件路径
FIELD_NAME_MAPPINGS_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'field_name_mappings.json')

# 常用词组词典（可以不断扩展）
WORD_DICTIONARY = {
    # 基础词汇
    '姓名': 'name',
    '名字': 'name',
    '性别': 'gender',
    '年龄': 'age',
    '电话': 'phone',
    '手机': 'mobile',
    '地址': 'address',
    '邮箱': 'email',
    '邮编': 'zipcode',
    '传真': 'fax',
    '备注': 'remark',
    '说明': 'description',
    '状态': 'status',
    '类型': 'type',
    '类别': 'category',
    '等级': 'level',
    '排序': 'sort_order',
    '序号': 'sequence',
    '编号': 'code',
    '编码': 'code',
    
    # 身份证相关
    '身份证': 'id_card',
    '身份证号': 'id_card',
    '身份证号码': 'id_card',
    '证件号': 'id_number',
    
    # 日期相关
    '日期': 'date',
    '时间': 'time',
    '年': 'year',
    '月': 'month',
    '日': 'day',
    '出生': 'birth',
    '出生日期': 'birth_date',
    '入职': 'hire',
    '入职日期': 'hire_date',
    '参加工作': 'work_start',
    '参加工作日期': 'work_start_date',
    '进入': 'entry',
    '进入单位': 'entry_unit',
    '进入本单位': 'entry_unit',
    '进入本单位日期': 'entry_date',
    '创建': 'create',
    '创建时间': 'created_at',
    '更新': 'update',
    '更新时间': 'updated_at',
    '登记': 'register',
    '登记日期': 'register_date',
    
    # 档案相关
    '档案': 'archive',
    '档案出生日期': 'archive_birth_date',
    '档案编号': 'archive_code',
    
    # 民族籍贯
    '民族': 'ethnicity',
    '籍贯': 'native_place',
    '出生地': 'birthplace',
    '户籍': 'household',
    '户籍所在地': 'household_location',
    
    # 联系相关
    '联系': 'contact',
    '联系电话': 'contact_phone',
    '联系方式': 'contact_info',
    '紧急联系人': 'emergency_contact',
    '紧急联系电话': 'emergency_phone',
    
    # 工作相关
    '工作': 'work',
    '单位': 'unit',
    '部门': 'department',
    '科室': 'section',
    '职位': 'position',
    '职务': 'job_title',
    '岗位': 'post',
    '职称': 'professional_title',
    '职级': 'job_level',
    '任职': 'appointment',
    '任职状态': 'employment_status',
    '在职': 'active',
    '离职': 'resigned',
    '退休': 'retired',
    
    # 教育相关
    '学历': 'education',
    '学位': 'degree',
    '毕业': 'graduate',
    '毕业院校': 'graduate_school',
    '专业': 'major',
    '学校': 'school',
    '学院': 'college',
    
    # 薪资相关
    '工资': 'salary',
    '基本工资': 'base_salary',
    '薪资': 'pay',
    '薪酬': 'compensation',
    '奖金': 'bonus',
    '津贴': 'allowance',
    '补贴': 'subsidy',
    '五险一金': 'insurance_fund',
    
    # 考核相关
    '考核': 'assessment',
    '绩效': 'performance',
    '考核结果': 'assessment_result',
    '考核等级': 'assessment_level',
    '考核日期': 'assessment_date',
    
    # 培训相关
    '培训': 'training',
    '培训内容': 'training_content',
    '培训机构': 'training_institution',
    '培训日期': 'training_date',
    '培训结果': 'training_result',
    
    # 合同相关
    '合同': 'contract',
    '合同编号': 'contract_code',
    '合同类型': 'contract_type',
    '合同开始日期': 'contract_start',
    '合同结束日期': 'contract_end',
    '合同期限': 'contract_term',
    
    # 调动相关
    '调动': 'transfer',
    '调动日期': 'transfer_date',
    '调出单位': 'from_unit',
    '调入单位': 'to_unit',
    '调动原因': 'transfer_reason',
    
    # 奖惩相关
    '奖励': 'reward',
    '惩罚': 'punishment',
    '处分': 'disciplinary',
    '奖惩日期': 'reward_date',
    '奖惩原因': 'reward_reason',
    
    # 家庭相关
    '家庭': 'family',
    '家庭住址': 'home_address',
    '婚姻': 'marital',
    '婚姻状况': 'marital_status',
    '配偶': 'spouse',
    '子女': 'children',
    '父母': 'parents',
    
    # 健康相关
    '健康': 'health',
    '体检': 'physical_exam',
    '体检日期': 'exam_date',
    '体检结果': 'exam_result',
    '血型': 'blood_type',
    '身高': 'height',
    '体重': 'weight',
    
    # 政治面貌
    '政治': 'political',
    '政治面貌': 'political_status',
    '党员': 'party_member',
    '团员': 'league_member',
    '群众': 'masses',
    '入党': 'join_party',
    '入党日期': 'join_party_date',
    
    # 其他常用
    '照片': 'photo',
    '头像': 'avatar',
    '签名': 'signature',
    '密码': 'password',
    '账号': 'account',
    '用户名': 'username',
    '角色': 'role',
    '权限': 'permission',
    '部门负责人': 'dept_manager',
    '直接上级': 'direct_supervisor',
    '办公电话': 'office_phone',
    '办公地址': 'office_address',
    '邮政编码': 'postal_code',
    '工号': 'employee_id',
    '员工编号': 'employee_code',
    '人员编号': 'personnel_code',
    '人员类别': 'personnel_category',
    '人员状态': 'personnel_status',
}


class FieldNameManager:
    """字段名管理器 - 管理中文字段名到英文字段名的映射"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.field_mappings = self._load_mappings()
        print("字段名管理器初始化完成（离线模式）")
    
    def _load_mappings(self) -> Dict:
        """加载字段名映射"""
        if os.path.exists(FIELD_NAME_MAPPINGS_FILE):
            try:
                with open(FIELD_NAME_MAPPINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载字段名映射失败: {e}")
        return {"mappings": {}, "reverse_mappings": {}}
    
    def _save_mappings(self):
        """保存字段名映射"""
        try:
            os.makedirs(os.path.dirname(FIELD_NAME_MAPPINGS_FILE), exist_ok=True)
            with open(FIELD_NAME_MAPPINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.field_mappings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存字段名映射失败: {e}")
    
    def _smart_translate(self, chinese_name: str) -> str:
        """
        智能翻译中文字段名
        使用词典匹配 + 分词组合
        """
        chinese_name = chinese_name.strip()
        
        # 1. 首先检查完整匹配
        if chinese_name in WORD_DICTIONARY:
            return WORD_DICTIONARY[chinese_name]
        
        # 2. 尝试分词组合（从长到短匹配）
        result_parts = []
        remaining = chinese_name
        
        # 按长度从长到短排序词典键
        sorted_words = sorted(WORD_DICTIONARY.keys(), key=len, reverse=True)
        
        while remaining:
            matched = False
            for word in sorted_words:
                if remaining.startswith(word):
                    result_parts.append(WORD_DICTIONARY[word])
                    remaining = remaining[len(word):]
                    matched = True
                    break
            
            if not matched:
                # 没有匹配到，跳过第一个字符
                remaining = remaining[1:]
        
        if result_parts:
            return '_'.join(result_parts)
        
        # 3. 最后的后备：使用拼音
        return self._to_pinyin(chinese_name)
    
    def _to_pinyin(self, chinese_name: str) -> str:
        """将中文转换为拼音（最后的后备方案）"""
        try:
            from pypinyin import pinyin, Style
            py_list = pinyin(chinese_name, style=Style.NORMAL)
            pinyin_str = '_'.join([item[0] for item in py_list])
            result = pinyin_str.lower().replace(' ', '_')
            result = re.sub(r'_+', '_', result)
            return result
        except Exception as e:
            print(f"拼音转换失败: {e}")
            # 最后的最后：使用字段序号
            return f"field_{len(self.field_mappings.get('mappings', {})) + 1}"
    
    def _generate_english_name(self, chinese_name: str) -> str:
        """
        生成英文字段名
        使用智能翻译，保证任何情况下都能生成有意义的字段名
        """
        # 如果已有映射，直接返回
        if chinese_name in self.field_mappings.get("mappings", {}):
            return self.field_mappings["mappings"][chinese_name]
        
        # 智能翻译
        english_name = self._smart_translate(chinese_name)
        
        # 检查是否冲突，如果冲突添加序号
        base_name = english_name
        counter = 1
        while english_name in self.field_mappings.get("reverse_mappings", {}):
            english_name = f"{base_name}_{counter}"
            counter += 1
        
        # 保存映射
        if "mappings" not in self.field_mappings:
            self.field_mappings["mappings"] = {}
        if "reverse_mappings" not in self.field_mappings:
            self.field_mappings["reverse_mappings"] = {}
            
        self.field_mappings["mappings"][chinese_name] = english_name
        self.field_mappings["reverse_mappings"][english_name] = chinese_name
        self._save_mappings()
        
        print(f"字段名映射: {chinese_name} -> {english_name}")
        return english_name
    
    def get_english_name(self, chinese_name: str) -> str:
        """
        获取中文字段名对应的英文字段名
        如果不存在，自动生成并保存
        """
        chinese_name = chinese_name.strip()
        
        # 检查是否已有映射
        if chinese_name in self.field_mappings.get("mappings", {}):
            return self.field_mappings["mappings"][chinese_name]
        
        # 生成新的映射
        return self._generate_english_name(chinese_name)
    
    def get_chinese_name(self, english_name: str) -> Optional[str]:
        """获取英文字段名对应的中文字段名"""
        return self.field_mappings.get("reverse_mappings", {}).get(english_name)
    
    def process_field_configs(self, field_configs: list) -> list:
        """
        处理字段配置列表，为每个字段添加英文字段名
        """
        processed_configs = []
        for field in field_configs:
            chinese_name = field.get('chinese_name') or field.get('sourceField') or field.get('source_name', '')
            if chinese_name:
                english_name = self.get_english_name(chinese_name)
                field_copy = field.copy()
                field_copy['english_name'] = english_name
                field_copy['targetField'] = english_name
                processed_configs.append(field_copy)
            else:
                processed_configs.append(field)
        return processed_configs


# 全局字段名管理器实例
field_name_manager = FieldNameManager()
