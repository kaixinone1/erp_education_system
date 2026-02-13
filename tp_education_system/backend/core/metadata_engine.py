"""
元数据引擎 - 负责表名翻译和字段映射管理
"""
import json
import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

# 核心实体词典 - 定义数据主体
CORE_ENTITY_DICT = {
    "教师": "teacher",
    "学生": "student",
    "员工": "employee",
    "党员": "party_member",
    "课程": "course",
    "数据": "data",
    "年级": "grade",
    "班级": "class",
    "学历": "education",
    "职称": "title",
    "职务": "position",
    "资格证": "certificate",
    "单位": "unit",
    "身份证": "id_card",
    "人才": "talent",
    "考勤": "attendance",
    "党建": "party_building",
    "活动": "activity",
    "人事": "hr",
    "工资": "salary",
    "部门": "department"
}

# 核心实体优先级（按匹配优先级排序）
CORE_ENTITY_PRIORITY = [
    "教师基础信息", "教师", "学生", "员工", "党员", "人事", "工资", "党建",
    "课程", "年级", "班级", "学历", "职称", "职务", "资格证",
    "考勤", "活动", "部门", "单位", "数据"
]

# 业务对象词典 - 定义数据类型
BUSINESS_OBJECT_DICT = {
    "基础信息": "basic_info",
    "基础数据": "basic_data",
    "个人身份": "personal_identity",
    "职务字典": "position_dictionary",
    "报表": "report",
    "记录": "record",
    "关系": "relation",
    "字典": "dictionary",
    "明细": "detail",
    "考勤明细": "attendance_detail",
    "信息": "info",
    "数据": "data",
    "管理": "management",
    "统计": "statistics",
    "汇总": "summary",
    "分析": "analysis",
    "档案": "archive",
    "证书": "certificate",
    "证明": "proof",
    "合同": "contract",
    "考核": "assessment",
    "评价": "evaluation",
    "培训": "training",
    "调动": "transfer",
    "离职": "resignation",
    "退休": "retirement",
    "招聘": "recruitment",
    "入职": "onboarding",
    "类型": "type",
    "层次": "level",
    "类别": "category",
    "等级": "grade"
}

# 全局字段映射 - 常用字段统一映射
GLOBAL_FIELD_MAPPINGS = {
    "姓名": "name",
    "名字": "name",
    "身份证号码": "id_card",
    "身份证号": "id_card",
    "身份证": "id_card",
    "出生日期": "birth_date",
    "档案出生日期": "file_birth_date",
    "身份证出生日期": "id_card_birth_date",
    "民族": "ethnicity",
    "籍贯": "native_place",
    "户籍所在地": "household_registration",
    "户籍": "household_registration",
    "联系电话": "phone",
    "手机号": "mobile_phone",
    "手机": "mobile_phone",
    "办公电话": "office_phone",
    "家庭电话": "home_phone",
    "学历": "education_level",
    "学历层次": "education_level",
    "学位": "degree",
    "专业": "major",
    "毕业院校": "graduated_school",
    "毕业学校": "graduated_school",
    "毕业时间": "graduation_date",
    "参加工作日期": "join_work_date",
    "参加工作时间": "join_work_date",
    "进入本单位日期": "enter_company_date",
    "进入单位时间": "enter_company_date",
    "任职状态": "employment_status",
    "工作状态": "employment_status",
    "状态": "status",
    "性别": "gender",
    "年龄": "age",
    "政治面貌": "political_status",
    "入党时间": "party_join_date",
    "入党日期": "party_join_date",
    "职称": "professional_title",
    "职务": "position",
    "岗位": "post",
    "部门": "department",
    "科室": "section",
    "学校": "school",
    "单位": "unit",
    "地址": "address",
    "邮箱": "email",
    "电子邮箱": "email",
    "QQ": "qq",
    "微信": "wechat",
    "备注": "remark",
    "说明": "description",
    "创建时间": "created_at",
    "更新时间": "updated_at",
    "创建人": "created_by",
    "更新人": "updated_by"
}

# 数据类型映射
DATA_TYPE_MAPPING = {
    "字符串": "VARCHAR",
    "文本": "TEXT",
    "整数": "INTEGER",
    "小数": "DECIMAL",
    "金额": "DECIMAL(10,2)",
    "日期": "DATE",
    "日期时间": "TIMESTAMP",
    "时间": "TIME",
    "布尔": "BOOLEAN",
    "是/否": "BOOLEAN",
    "图片": "TEXT",
    "文件": "TEXT",
    "枚举": "VARCHAR"
}


class MetadataEngine:
    """元数据引擎 - 管理表名翻译和字段映射"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        self.config_dir = config_dir
        self.field_mappings_file = os.path.join(config_dir, 'field_mappings.json')
        self.table_schemas_file = os.path.join(config_dir, 'table_schemas.json')
        
        # 加载配置
        self.field_mappings = self._load_field_mappings()
        self.table_schemas = self._load_table_schemas()
    
    def _get_existing_tables_from_db(self) -> List[str]:
        """从数据库查询真实存在的表列表"""
        try:
            # 使用SQLAlchemy查询数据库中的所有表
            from sqlalchemy import create_engine, text
            
            DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
            engine = create_engine(DATABASE_URL)
            
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
                return tables
        except Exception as e:
            print(f"从数据库查询表列表失败: {e}")
            # 如果查询失败，回退到从配置文件获取
            return list(self.table_schemas.get("tables", {}).keys())
    
    def _load_json(self, file_path: str) -> dict:
        """加载JSON文件"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
        return {}
    
    def _save_json(self, file_path: str, data: dict):
        """保存JSON文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存文件失败 {file_path}: {e}")
            return False
    
    def _load_field_mappings(self) -> dict:
        """加载字段映射配置"""
        data = self._load_json(self.field_mappings_file)
        if not data:
            data = {
                "configs": [],
                "global_mappings": GLOBAL_FIELD_MAPPINGS,
                "usage_stats": {}
            }
        return data
    
    def _load_table_schemas(self) -> dict:
        """加载表结构定义"""
        data = self._load_json(self.table_schemas_file)
        if not data:
            data = {"tables": {}}
        return data
    
    def save_configs(self):
        """保存所有配置"""
        self._save_json(self.field_mappings_file, self.field_mappings)
        self._save_json(self.table_schemas_file, self.table_schemas)
    
    def translate_table_name(self, chinese_name: str, module_name: str = "", table_type: str = "master") -> str:
        """
        将中文表名翻译为英文表名
        使用智能分词组合，实现全文精准翻译
        格式: [模块前缀][核心实体]_[业务对象1]_[业务对象2]_...，全部小写
        :param chinese_name: 中文表名
        :param module_name: 模块名称
        :param table_type: 表类型 (master/child/dictionary)
        :return: 英文表名
        """
        # 清理表名
        cleaned_name = chinese_name.strip()

        # 1. 确定模块前缀
        module_prefix = ""
        if module_name:
            module_prefix = self._get_module_prefix(module_name)

        # 2. 使用智能分词翻译，获取所有匹配的部分
        translated_parts = self._smart_translate_table_name(cleaned_name)

        # 3. 判断是否为字典表
        is_dictionary = table_type == "dictionary" or any(keyword in cleaned_name for keyword in ["字典", "类型", "层次", "类别"])

        # 4. 组合格式化
        if is_dictionary:
            # 字典表添加 dict_ 前缀
            english_name = f"{module_prefix}dict_{'_'.join(translated_parts)}".lower()
        else:
            english_name = f"{module_prefix}{'_'.join(translated_parts)}".lower()

        # 5. 清理非法字符
        english_name = re.sub(r'[^a-z0-9_]', '_', english_name)
        english_name = re.sub(r'_+', '_', english_name)  # 合并多个下划线
        english_name = english_name.strip('_')
        
        # 5. 清理非法字符
        english_name = re.sub(r'[^a-z0-9_]', '_', english_name)
        english_name = re.sub(r'_+', '_', english_name)  # 合并多个下划线
        english_name = english_name.strip('_')
        
        # 6. 确保唯一性 - 使用智能命名策略，不使用序号后缀
        # 从数据库查询真实存在的表，而不是依赖内存缓存
        existing_tables = self._get_existing_tables_from_db()
        if english_name in existing_tables:
            # 尝试使用同义词替换
            english_name = self._generate_unique_table_name(
                english_name, cleaned_name, module_prefix, existing_tables
            )
        
        return english_name

    def _smart_translate_table_name(self, chinese_name: str) -> List[str]:
        """
        智能分词翻译表名
        将中文表名分解为多个部分，分别翻译后组合
        例如："学历类型字典" -> ["education", "type", "dictionary"]
        """
        cleaned_name = chinese_name.strip()
        translated_parts = []
        remaining = cleaned_name

        # 构建完整的词典（核心实体 + 业务对象）
        full_dictionary = {}
        full_dictionary.update(CORE_ENTITY_DICT)
        full_dictionary.update(BUSINESS_OBJECT_DICT)

        # 按长度从长到短排序，优先匹配长词
        sorted_words = sorted(full_dictionary.keys(), key=len, reverse=True)

        # 用于跟踪已匹配的位置，避免重叠匹配
        matched_positions = set()

        # 第一轮：找出所有匹配的词汇及其位置
        matches = []
        for word in sorted_words:
            pos = 0
            while pos < len(remaining):
                idx = remaining.find(word, pos)
                if idx == -1:
                    break

                # 检查这个位置是否已经被匹配
                is_overlapping = any(idx <= p < idx + len(word) for p in matched_positions)

                if not is_overlapping:
                    matches.append({
                        'word': word,
                        'translation': full_dictionary[word],
                        'position': idx,
                        'length': len(word)
                    })
                    # 标记已匹配的位置
                    for p in range(idx, idx + len(word)):
                        matched_positions.add(p)

                pos = idx + 1

        # 按位置排序匹配结果
        matches.sort(key=lambda x: x['position'])

        # 提取翻译结果
        for match in matches:
            translated_parts.append(match['translation'])

        # 如果没有匹配到任何内容，使用默认值
        if not translated_parts:
            translated_parts = ["data"]

        return translated_parts

    def _generate_unique_table_name(self, base_name: str, chinese_name: str,
                                    module_prefix: str, existing_tables: List[str]) -> str:
        """
        生成唯一的表名，使用智能策略避免序号后缀
        """
        # 同义词替换策略
        synonyms = {
            "info": ["information", "data", "details", "profile"],
            "data": ["info", "information", "records", "dataset"],
            "basic": ["foundation", "primary", "main", "core"],
            "detail": ["detailed", "specifics", "particulars", "extended"],
            "record": ["log", "history", "archive", "chronicle"],
            "management": ["mgmt", "admin", "administration", "control"]
        }
        
        # 尝试同义词替换
        for word, alternatives in synonyms.items():
            if word in base_name:
                for alt in alternatives:
                    new_name = base_name.replace(word, alt)
                    if new_name not in existing_tables:
                        return new_name
        
        # 添加更多描述词
        descriptive_words = ["personal", "work", "education", "salary", 
                            "professional", "employment", "career", "staff"]
        
        for desc_word in descriptive_words:
            # 在前面添加描述词
            new_name = f"{desc_word}_{base_name}"
            if new_name not in existing_tables:
                return new_name
            
            # 在后面添加描述词
            new_name = f"{base_name}_{desc_word}"
            if new_name not in existing_tables:
                return new_name
        
        # 如果所有策略都失败，使用模块名+完整中文名拼音（简化）
        # 这是一个保底方案，实际应该很少用到
        simplified_chinese = re.sub(r'[^\u4e00-\u9fff]', '', chinese_name)
        if simplified_chinese:
            # 使用中文名的哈希值作为后缀（比_1, _2更有意义）
            name_hash = str(hash(simplified_chinese))[:6]
            new_name = f"{base_name}_{name_hash}"
            if new_name not in existing_tables:
                return new_name
        
        # 最后的保底：使用时间戳（确保唯一性）
        timestamp = datetime.now().strftime("%Y%m%d")
        new_name = f"{base_name}_{timestamp}"
        counter = 1
        final_name = new_name
        while final_name in existing_tables:
            final_name = f"{new_name}_{counter}"
            counter += 1
        
        return final_name
    
    def _get_module_prefix(self, module_name: str) -> str:
        """获取模块前缀"""
        module_prefixes = {
            "人事管理": "hr_",
            "工资管理": "salary_",
            "党建管理": "party_",
            "学生管理": "student_",
            "系统管理": "system_",
            "教师管理": "teacher_",
            "数据中心": "data_",
            "部门管理": "dept_",
            "考勤管理": "attendance_"
        }
        return module_prefixes.get(module_name, "")
    
    def translate_field_name(self, chinese_name: str) -> str:
        """
        将中文字段名翻译为英文字段名
        """
        # 1. 首先检查全局映射
        if chinese_name in GLOBAL_FIELD_MAPPINGS:
            return GLOBAL_FIELD_MAPPINGS[chinese_name]
        
        # 2. 尝试智能匹配（包含关系）
        for cn_field, en_field in sorted(GLOBAL_FIELD_MAPPINGS.items(), key=lambda x: len(x[0]), reverse=True):
            if cn_field in chinese_name or chinese_name in cn_field:
                return en_field
        
        # 3. 使用拼音转换（简化处理）
        # 实际项目中可以使用 pypinyin 库
        # 这里使用简单的翻译规则
        english_name = self._simple_translate(chinese_name)
        
        # 4. 格式化
        english_name = english_name.lower()
        english_name = re.sub(r'[^a-z0-9_]', '_', english_name)
        english_name = re.sub(r'_+', '_', english_name)
        english_name = english_name.strip('_')
        
        return english_name or "field_" + str(hash(chinese_name))[:8]
    
    def _simple_translate(self, chinese: str) -> str:
        """简单的中文到英文转换"""
        # 常见词汇映射
        common_words = {
            "编号": "code",
            "代码": "code",
            "名称": "name",
            "类型": "type",
            "类别": "category",
            "等级": "level",
            "状态": "status",
            "日期": "date",
            "时间": "time",
            "年": "year",
            "月": "month",
            "日": "day",
            "数量": "quantity",
            "金额": "amount",
            "价格": "price",
            "比例": "ratio",
            "百分比": "percentage",
            "分数": "score",
            "等级": "grade",
            "级别": "level",
            "序号": "seq",
            "顺序": "order",
            "排序": "sort_order"
        }
        
        result = chinese
        for cn, en in sorted(common_words.items(), key=lambda x: len(x[0]), reverse=True):
            result = result.replace(cn, en)
        
        # 如果还有中文字符，使用拼音首字母
        if re.search(r'[\u4e00-\u9fff]', result):
            result = self._pinyin_initials(chinese)
        
        return result
    
    def _pinyin_initials(self, chinese: str) -> str:
        """获取拼音首字母"""
        # 简化实现，实际使用 pypinyin 库
        try:
            from pypinyin import pinyin, Style
            initials = pinyin(chinese, style=Style.FIRST_LETTER)
            return ''.join([p[0] for p in initials])
        except:
            # 如果没有pypinyin，使用简单映射
            return "field_" + str(hash(chinese))[:8]
    
    def get_field_mapping_config(self, source_file_pattern: str) -> Optional[dict]:
        """根据源文件模式获取字段映射配置"""
        configs = self.field_mappings.get("configs", [])
        for config in configs:
            if config.get("source_file_pattern") == source_file_pattern:
                return config
        return None
    
    def save_field_mapping_config(self, config: dict):
        """保存字段映射配置"""
        configs = self.field_mappings.get("configs", [])
        
        # 检查是否已存在
        existing_idx = None
        for idx, existing in enumerate(configs):
            if existing.get("source_file_pattern") == config.get("source_file_pattern"):
                existing_idx = idx
                break
        
        # 添加元数据
        config["updated_at"] = datetime.now().isoformat()
        if existing_idx is None:
            config["created_at"] = datetime.now().isoformat()
            config["version"] = 1
            configs.append(config)
        else:
            config["created_at"] = configs[existing_idx].get("created_at", datetime.now().isoformat())
            config["version"] = configs[existing_idx].get("version", 1) + 1
            configs[existing_idx] = config
        
        self.field_mappings["configs"] = configs
        self._save_json(self.field_mappings_file, self.field_mappings)
    
    def record_field_usage(self, chinese_field: str, english_field: str):
        """记录字段映射使用情况"""
        stats = self.field_mappings.get("usage_stats", {})
        key = f"{chinese_field}->{english_field}"
        stats[key] = stats.get(key, 0) + 1
        self.field_mappings["usage_stats"] = stats
        self._save_json(self.field_mappings_file, self.field_mappings)
    
    def get_suggested_field_mapping(self, chinese_field: str) -> Optional[str]:
        """获取建议的字段映射"""
        # 1. 检查全局映射
        if chinese_field in GLOBAL_FIELD_MAPPINGS:
            return GLOBAL_FIELD_MAPPINGS[chinese_field]
        
        # 2. 检查使用统计
        stats = self.field_mappings.get("usage_stats", {})
        best_match = None
        best_count = 0
        
        for key, count in stats.items():
            if key.startswith(chinese_field + "->"):
                if count > best_count:
                    best_count = count
                    best_match = key.split("->")[1]
        
        return best_match
    
    def save_table_schema(self, table_name: str, schema: dict):
        """保存表结构定义"""
        tables = self.table_schemas.get("tables", {})
        schema["updated_at"] = datetime.now().isoformat()
        if table_name not in tables:
            schema["created_at"] = datetime.now().isoformat()
        tables[table_name] = schema
        self.table_schemas["tables"] = tables
        self._save_json(self.table_schemas_file, self.table_schemas)
    
    def get_table_schema(self, table_name: str) -> Optional[dict]:
        """获取表结构定义"""
        return self.table_schemas.get("tables", {}).get(table_name)
    
    def auto_map_fields(self, chinese_fields: List[str], module_name: str = "") -> List[dict]:
        """
        自动映射中文字段到英文字段
        返回映射结果列表
        """
        mappings = []
        for field in chinese_fields:
            # 1. 尝试全局映射
            english_name = GLOBAL_FIELD_MAPPINGS.get(field)
            
            # 2. 尝试智能匹配
            if not english_name:
                english_name = self.get_suggested_field_mapping(field)
            
            # 3. 自动翻译
            if not english_name:
                english_name = self.translate_field_name(field)
            
            # 推断数据类型
            data_type = self._infer_data_type(field, english_name)
            
            mappings.append({
                "source_field": field,
                "target_field": english_name,
                "data_type": data_type,
                "is_required": self._is_required_field(field),
                "is_unique": self._is_unique_field(field),
                "confidence": "high" if field in GLOBAL_FIELD_MAPPINGS else "medium"
            })
        
        return mappings
    
    def _infer_data_type(self, chinese_field: str, english_field: str) -> str:
        """推断字段数据类型"""
        # 根据字段名推断类型
        if any(keyword in chinese_field for keyword in ["日期", "时间", "生日"]):
            return "DATE"
        elif any(keyword in chinese_field for keyword in ["号码", "电话", "手机", "身份证", "编号", "代码"]):
            return "VARCHAR(255)"
        elif any(keyword in chinese_field for keyword in ["金额", "工资", "价格"]):
            return "DECIMAL(10,2)"
        elif any(keyword in chinese_field for keyword in ["数量", "人数", "次数", "年数"]):
            return "INTEGER"
        elif any(keyword in chinese_field for keyword in ["备注", "说明", "描述"]):
            return "TEXT"
        else:
            return "VARCHAR(255)"
    
    def _is_required_field(self, chinese_field: str) -> bool:
        """判断是否为必填字段"""
        required_keywords = ["姓名", "名称", "编号", "代码", "身份证", "日期"]
        return any(keyword in chinese_field for keyword in required_keywords)
    
    def _is_unique_field(self, chinese_field: str) -> bool:
        """判断是否为唯一字段"""
        unique_keywords = ["身份证", "编号", "代码", "手机号"]
        return any(keyword in chinese_field for keyword in unique_keywords)


# 全局元数据引擎实例
_metadata_engine = None

def get_metadata_engine() -> MetadataEngine:
    """获取全局元数据引擎实例"""
    global _metadata_engine
    if _metadata_engine is None:
        _metadata_engine = MetadataEngine()
    return _metadata_engine
