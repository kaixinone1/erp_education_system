"""
中文表名转英文表名工具 - 完整版
"""
import re

# 常用词汇映射 - 完整版
COMMON_WORDS = {
    # 人物相关
    "教师": "teacher",
    "学生": "student",
    "职工": "staff",
    "员工": "employee",
    "人员": "person",
    "校长": "principal",
    "主任": "director",
    "书记": "secretary",
    "局长": "director",
    "校长": "principal",
    
    # 组织相关
    "学校": "school",
    "教育局": "education_bureau",
    "机关": "agency",
    "事业单位": "public_institution",
    "单位": "unit",
    "部门": "department",
    
    # 人事相关
    "人事": "personnel",
    "档案": "archive",
    "简历": "resume",
    "招聘": "recruitment",
    "离职": "resignation",
    "入职": "onboarding",
    "调动": "transfer",
    "工作": "work",
    "任职": "appointment",
    "在编": "staffed",
    "合同": "contract",
    "临时": "temporary",
    "聘用": "employment",
    
    # 状态相关
    "在职": "active",
    "退休": "retired",
    "离休": "retired",
    "去世": "deceased",
    "死亡": "deceased",
    "调离": "transferred",
    "调出": "transferred_out",
    "离职": "left",
    "辞职": "resigned",
    
    # 业务相关
    "业务": "business",
    "事项": "matter",
    "事项": "affair",
    
    # 教育相关
    "教育": "education",
    "教学": "teaching",
    "学历": "education_background",
    "学位": "degree",
    "专业": "major",
    "学科": "subject",
    "课程": "course",
    "班级": "class",
    "年级": "grade",
    "学期": "semester",
    "成绩": "score",
    "考试": "exam",
    "考核": "assessment",
    "评价": "evaluation",
    
    # 资格资质
    "资格": "qualification",
    "资质": "qualification",
    "职称": "professional_title",
    "职务": "position",
    "岗位": "post",
    "级别": "level",
    "等级": "grade",
    
    # 薪酬相关
    "工资": "salary",
    "薪酬": "compensation",
    "绩效": "performance",
    "津贴": "allowance",
    "补贴": "subsidy",
    "奖金": "bonus",
    "待遇": "treatment",
    "养老": "pension",
    "保险": "insurance",
    "社保": "social_security",
    "医保": "medical_insurance",
    
    # 退休相关
    "退休": "retirement",
    "离休": "retirement",
    "呈报": "report",
    "呈报表": "report_form",
    "申报": "declaration",
    "审批": "approval",
    "审核": "review",
    "办理": "handle",
    "核发": "issue",
    
    # 通用词汇
    "信息": "info",
    "数据": "data",
    "记录": "record",
    "明细": "detail",
    "列表": "list",
    "汇总": "summary",
    "统计": "statistics",
    "查询": "query",
    "管理": "management",
    "系统": "system",
    "基础": "basic",
    "基本": "basic",
    "公共": "public",
    "临时": "temporary",
    "历史": "historical",
    "当前": "current",
    "全部": "all",
    "主要": "main",
    "辅助": "auxiliary",
    "相关": "related",
    "情况": "situation",
    "材料": "material",
    "文档": "document",
    "资料": "document",
    
    # 操作相关
    "新增": "add",
    "修改": "update",
    "删除": "delete",
    "导入": "import",
    "导出": "export",
    "打印": "print",
    "提交": "submit",
    "保存": "save",
    "确认": "confirm",
    "取消": "cancel",
    "审核": "audit",
    "审批": "approve",
    "签发": "issue",
    
    # 时间相关
    "时间": "time",
    "日期": "date",
    "年份": "year",
    "年度": "yearly",
    "月份": "month",
    "月": "month",
    "日": "day",
    "开始": "start",
    "结束": "end",
    "创建": "create",
    "更新": "update",
    "出生": "birth",
    "年龄": "age",
    
    # 地址相关
    "地址": "address",
    "籍贯": "native_place",
    "出生地": "birth_place",
    "现居": "current_residence",
    
    # 联系方式
    "电话": "phone",
    "手机": "mobile",
    "邮箱": "email",
    "地址": "address",
    
    # 身份相关
    "身份证": "id_card",
    "性别": "gender",
    "民族": "ethnicity",
    "政治": "political",
    "党派": "party",
    "党员": "party_member",
    
    # 其他常用
    "编号": "number",
    "代码": "code",
    "名称": "name",
    "姓名": "name",
    "标题": "title",
    "说明": "description",
    "备注": "remark",
    "备注": "note",
    "类型": "type",
    "类别": "category",
    "状态": "status",
    "顺序": "order",
    "排序": "sort",
    "金额": "amount",
    "数量": "quantity",
    "比例": "ratio",
    "百分比": "percentage",
}

def chinese_to_english(name: str) -> str:
    """
    将中文表名转换为英文表名
    
    规则：
    1. 先匹配最长词汇（最多5个字）
    2. 使用下划线连接
    3. 全部小写
    4. 去除特殊字符
    """
    if not name:
        return ""
    
    # 去除特殊字符，保留中文、英文、数字
    name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', name)
    
    result = []
    i = 0
    name_len = len(name)
    
    while i < name_len:
        # 尝试匹配最长的词汇（最多5个字）
        matched = False
        for length in range(min(5, name_len - i), 0, -1):
            substr = name[i:i+length]
            if substr in COMMON_WORDS:
                result.append(COMMON_WORDS[substr])
                i += length
                matched = True
                break
        
        if not matched:
            # 如果没有匹配到，跳过该中文字符
            char = name[i]
            if '\u4e00' <= char <= '\u9fff':
                # 是中文但不在词汇表中
                pass
            else:
                # 是英文或数字，直接使用
                result.append(char.lower())
            i += 1
    
    # 清理结果
    result_str = '_'.join(result)
    result_str = re.sub(r'_+', '_', result_str)
    result_str = result_str.strip('_')
    
    return result_str

def translate_table_name(name: str) -> str:
    """将中文表名翻译为英文表名"""
    english_name = chinese_to_english(name)
    
    # 确保不以数字开头
    if english_name and english_name[0].isdigit():
        english_name = 't_' + english_name
    
    return english_name
