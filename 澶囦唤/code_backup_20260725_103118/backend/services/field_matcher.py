"""
智能字段匹配引擎
自动匹配模板字段与系统字段
"""
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
import re


class FieldMatcher:
    """字段匹配器"""
    
    # 字段同义词库
    FIELD_SYNONYMS = {
        "姓名": ["name", "姓名", "名字", "teacher_name", "full_name"],
        "性别": ["gender", "性别", "sex", "teacher_gender"],
        "出生日期": ["birth_date", "出生日期", "出生年月", "birthday", "出生", "archive_birth_date"],
        "身份证号": ["id_card", "身份证号", "身份证号码", "身份证", "id_number", "identity_card"],
        "民族": ["ethnicity", "民族", "国籍", "nation", "teacher_ethnicity"],
        "籍贯": ["native_place", "籍贯", "出生地", "出生地", "birth_place"],
        "政治面貌": ["political_status", "政治面貌", "党派", "political"],
        "学历": ["education", "学历", "文化程度", "最高学历", "education_level"],
        "学位": ["degree", "学位", "最高学位", "academic_degree"],
        "专业": ["major", "专业", "所学专业", "specialty"],
        "毕业院校": ["school", "毕业院校", "学校", "院校", "毕业学校", "university"],
        "联系电话": ["phone", "联系电话", "电话", "手机", "手机号码", "contact_phone", "mobile"],
        "邮箱": ["email", "邮箱", "电子邮件", "e-mail", "mail"],
        "地址": ["address", "地址", "住址", "家庭住址", "home_address"],
        "工作单位": ["unit", "工作单位", "单位", "所在部门", "department"],
        "职务": ["position", "职务", "职位", "现任职务", "job_title"],
        "职称": ["title", "职称", "专业技术职务", "professional_title"],
        "参加工作时间": ["work_date", "参加工作时间", "工作日期", "入职时间", "work_start_date"],
        "工龄": ["work_years", "工龄", "工作年限", "工作年数"],
        "教龄": ["teaching_years", "教龄", "教学年限", "教学年数"],
        "基本工资": ["basic_salary", "基本工资", "基础工资", "岗位工资"],
        "薪级": ["salary_grade", "薪级", "薪级工资", "工资级别"],
        "津贴": ["allowance", "津贴", "补贴", "岗位津贴"],
        "绩效工资": ["performance_pay", "绩效工资", "绩效", "奖金"],
    }
    
    # 系统字段定义（从数据库获取）
    SYSTEM_FIELDS = [
        {"name": "teacher_basic_info.name", "label": "姓名", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.gender", "label": "性别", "type": "select", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.id_card", "label": "身份证号", "type": "id_card", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.birth_date", "label": "出生日期", "type": "date", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.archive_birth_date", "label": "档案出生日期", "type": "date", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.ethnicity", "label": "民族", "type": "select", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.native_place", "label": "籍贯", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.political_status", "label": "政治面貌", "type": "select", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.education", "label": "学历", "type": "select", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.degree", "label": "学位", "type": "select", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.major", "label": "专业", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.graduate_school", "label": "毕业院校", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.work_start_date", "label": "参加工作时间", "type": "date", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.contact_phone", "label": "联系电话", "type": "phone", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.email", "label": "邮箱", "type": "email", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.home_address", "label": "家庭住址", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.current_unit", "label": "现工作单位", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.position", "label": "职务", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.professional_title", "label": "职称", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.work_years", "label": "工龄", "type": "number", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.teaching_years", "label": "教龄", "type": "number", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.current_salary_grade", "label": "现执行薪级", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.retirement_salary_grade", "label": "退休时薪级", "type": "text", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.basic_salary", "label": "基本工资", "type": "number", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.allowance", "label": "津贴补贴", "type": "number", "table": "teacher_basic_info"},
        {"name": "teacher_basic_info.performance_pay", "label": "绩效工资", "type": "number", "table": "teacher_basic_info"},
    ]
    
    def __init__(self, system_fields: Optional[List[Dict]] = None):
        """
        初始化匹配器
        
        Args:
            system_fields: 系统字段列表，默认使用预定义列表
        """
        self.system_fields = system_fields or self.SYSTEM_FIELDS
    
    def match_fields(self, template_fields: List[Dict]) -> List[Dict]:
        """
        匹配模板字段与系统字段
        
        Args:
            template_fields: 模板提取的字段列表
            
        Returns:
            匹配结果列表：[{template_field, matched_field, confidence, method}]
        """
        results = []
        
        for template_field in template_fields:
            template_name = template_field.get("name", "")
            template_label = template_field.get("label", "")
            
            # 尝试多种匹配方法
            best_match = None
            best_confidence = 0
            best_method = ""
            
            for system_field in self.system_fields:
                # 方法1：直接名称匹配
                name_confidence = self._match_by_name(template_name, system_field)
                if name_confidence > best_confidence:
                    best_confidence = name_confidence
                    best_match = system_field
                    best_method = "name_match"
                
                # 方法2：标签匹配
                label_confidence = self._match_by_label(template_label, system_field)
                if label_confidence > best_confidence:
                    best_confidence = label_confidence
                    best_match = system_field
                    best_method = "label_match"
                
                # 方法3：同义词匹配
                synonym_confidence = self._match_by_synonym(template_name, system_field)
                if synonym_confidence > best_confidence:
                    best_confidence = synonym_confidence
                    best_match = system_field
                    best_method = "synonym_match"
                
                # 方法4：模糊匹配
                fuzzy_confidence = self._fuzzy_match(template_name, template_label, system_field)
                if fuzzy_confidence > best_confidence:
                    best_confidence = fuzzy_confidence
                    best_match = system_field
                    best_method = "fuzzy_match"
            
            result = {
                "template_field": template_field,
                "matched_field": best_match,
                "confidence": round(best_confidence, 2),
                "method": best_method,
                "status": "pending"  # pending, confirmed, rejected
            }
            results.append(result)
        
        # 按置信度排序
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return results
    
    def _match_by_name(self, template_name: str, system_field: Dict) -> float:
        """通过字段名匹配"""
        system_name = system_field.get("name", "").split(".")[-1]  # 取最后一部分
        
        # 完全匹配
        if template_name == system_name:
            return 1.0
        
        # 包含匹配
        if template_name in system_name or system_name in template_name:
            return 0.8
        
        # 相似度匹配
        similarity = SequenceMatcher(None, template_name, system_name).ratio()
        return similarity * 0.6
    
    def _match_by_label(self, template_label: str, system_field: Dict) -> float:
        """通过标签匹配"""
        system_label = system_field.get("label", "")
        
        # 完全匹配
        if template_label == system_label:
            return 1.0
        
        # 包含匹配
        if template_label in system_label or system_label in template_label:
            return 0.9
        
        # 相似度匹配
        similarity = SequenceMatcher(None, template_label, system_label).ratio()
        return similarity * 0.7
    
    def _match_by_synonym(self, template_name: str, system_field: Dict) -> float:
        """通过同义词匹配"""
        system_label = system_field.get("label", "")
        system_name = system_field.get("name", "").split(".")[-1]
        
        # 检查同义词库
        for standard_name, synonyms in self.FIELD_SYNONYMS.items():
            # 检查模板名是否在标准名的同义词中
            if any(syn in template_name for syn in synonyms):
                # 检查系统字段是否与标准名相关
                if standard_name in system_label or any(syn in system_label for syn in synonyms):
                    return 0.95
                if standard_name in system_name or any(syn in system_name for syn in synonyms):
                    return 0.85
        
        return 0.0
    
    def _fuzzy_match(self, template_name: str, template_label: str, system_field: Dict) -> float:
        """模糊匹配"""
        system_label = system_field.get("label", "")
        system_name = system_field.get("name", "").split(".")[-1]
        
        # 使用fuzzywuzzy进行模糊匹配
        name_ratio = fuzz.ratio(template_name, system_name)
        label_ratio = fuzz.ratio(template_label, system_label)
        name_partial = fuzz.partial_ratio(template_name, system_name)
        label_partial = fuzz.partial_ratio(template_label, system_label)
        
        # 综合得分
        max_ratio = max(name_ratio, label_ratio, name_partial, label_partial)
        return max_ratio / 100.0 * 0.8  # 最高0.8分
    
    def get_field_value(self, field_name: str, teacher_data: Dict) -> Any:
        """
        从教师数据中获取字段值
        
        Args:
            field_name: 字段名（如 teacher_basic_info.name）
            teacher_data: 教师数据字典
            
        Returns:
            字段值
        """
        parts = field_name.split(".")
        if len(parts) == 2:
            table, column = parts
            if table in teacher_data:
                return teacher_data[table].get(column)
        return None
    
    def apply_dictionary_mapping(self, value: Any, field_type: str) -> str:
        """
        应用字典表映射（代码转名称）
        
        Args:
            value: 原始值（代码）
            field_type: 字段类型
            
        Returns:
            转换后的名称
        """
        # 字典表映射（简化版）
        dictionary_maps = {
            "gender": {"1": "男", "2": "女", "M": "男", "F": "女"},
            "political_status": {
                "01": "中共党员", "02": "中共预备党员", "03": "共青团员",
                "04": "民革党员", "05": "民盟盟员", "06": "民建会员",
                "07": "民进会员", "08": "农工党党员", "09": "致公党党员",
                "10": "九三学社社员", "11": "台盟盟员", "12": "无党派人士",
                "13": "群众"
            },
            "ethnicity": {
                "01": "汉族", "02": "蒙古族", "03": "回族", "04": "藏族",
                "05": "维吾尔族", "06": "苗族", "07": "彝族", "08": "壮族",
                "09": "布依族", "10": "朝鲜族", "11": "满族", "12": "侗族",
                "13": "瑶族", "14": "白族", "15": "土家族", "16": "哈尼族",
                "17": "哈萨克族", "18": "傣族", "19": "黎族", "20": "傈僳族",
                "21": "佤族", "22": "畲族", "23": "高山族", "24": "拉祜族",
                "25": "水族", "26": "东乡族", "27": "纳西族", "28": "景颇族",
                "29": "柯尔克孜族", "30": "土族", "31": "达斡尔族", "32": "仫佬族",
                "33": "羌族", "34": "布朗族", "35": "撒拉族", "36": "毛南族",
                "37": "仡佬族", "38": "锡伯族", "39": "阿昌族", "40": "普米族",
                "41": "塔吉克族", "42": "怒族", "43": "乌孜别克族", "44": "俄罗斯族",
                "45": "鄂温克族", "46": "德昂族", "47": "保安族", "48": "裕固族",
                "49": "京族", "50": "塔塔尔族", "51": "独龙族", "52": "鄂伦春族",
                "53": "赫哲族", "54": "门巴族", "55": "珞巴族", "56": "基诺族"
            },
            "education": {
                "01": "博士研究生", "02": "硕士研究生", "03": "本科",
                "04": "专科", "05": "中专", "06": "高中", "07": "初中",
                "08": "小学", "09": "其他"
            },
            "degree": {
                "01": "博士", "02": "硕士", "03": "学士", "04": "无学位"
            }
        }
        
        if field_type in dictionary_maps and str(value) in dictionary_maps[field_type]:
            return dictionary_maps[field_type][str(value)]
        
        return str(value) if value is not None else ""


def match_template_fields(template_fields: List[Dict], system_fields: Optional[List[Dict]] = None) -> List[Dict]:
    """
    便捷函数：匹配模板字段
    
    Args:
        template_fields: 模板字段列表
        system_fields: 系统字段列表（可选）
        
    Returns:
        匹配结果
    """
    matcher = FieldMatcher(system_fields)
    return matcher.match_fields(template_fields)
