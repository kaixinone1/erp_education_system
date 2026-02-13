from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
from typing import List, Dict, Any

router = APIRouter(prefix="/api/import", tags=["import"])

# 智能映射规则库：中文字段名 -> 英文字段名和数据类型
FIELD_MAPPING_RULES = {
    # 基础信息字段
    "姓名": {"target_field": "name", "data_type": "VARCHAR", "length": 50},
    "名字": {"target_field": "name", "data_type": "VARCHAR", "length": 50},
    "性别": {"target_field": "gender", "data_type": "VARCHAR", "length": 10},
    "年龄": {"target_field": "age", "data_type": "INTEGER"},
    "出生日期": {"target_field": "birth_date", "data_type": "DATE"},
    "生日": {"target_field": "birth_date", "data_type": "DATE"},
    
    # 身份证相关
    "身份证号": {"target_field": "id_card", "data_type": "VARCHAR", "length": 18},
    "身份证号码": {"target_field": "id_card", "data_type": "VARCHAR", "length": 18},
    "身份证": {"target_field": "id_card", "data_type": "VARCHAR", "length": 18},
    
    # 联系方式
    "电话": {"target_field": "phone", "data_type": "VARCHAR", "length": 20},
    "联系电话": {"target_field": "phone", "data_type": "VARCHAR", "length": 20},
    "手机": {"target_field": "mobile", "data_type": "VARCHAR", "length": 20},
    "手机号码": {"target_field": "mobile", "data_type": "VARCHAR", "length": 20},
    "邮箱": {"target_field": "email", "data_type": "VARCHAR", "length": 100},
    "电子邮箱": {"target_field": "email", "data_type": "VARCHAR", "length": 100},
    
    # 地址信息
    "地址": {"target_field": "address", "data_type": "VARCHAR", "length": 200},
    "家庭地址": {"target_field": "home_address", "data_type": "VARCHAR", "length": 200},
    "工作单位": {"target_field": "work_unit", "data_type": "VARCHAR", "length": 100},
    "单位": {"target_field": "work_unit", "data_type": "VARCHAR", "length": 100},
    
    # 教育信息
    "学历": {"target_field": "education", "data_type": "VARCHAR", "length": 20},
    "学位": {"target_field": "degree", "data_type": "VARCHAR", "length": 20},
    "毕业院校": {"target_field": "school", "data_type": "VARCHAR", "length": 100},
    "专业": {"target_field": "major", "data_type": "VARCHAR", "length": 50},
    
    # 工作信息
    "职称": {"target_field": "title", "data_type": "VARCHAR", "length": 30},
    "职务": {"target_field": "position", "data_type": "VARCHAR", "length": 30},
    "部门": {"target_field": "department", "data_type": "VARCHAR", "length": 50},
    "入职日期": {"target_field": "hire_date", "data_type": "DATE"},
    "参加工作时间": {"target_field": "work_date", "data_type": "DATE"},
    
    # 工资信息
    "基本工资": {"target_field": "base_salary", "data_type": "DECIMAL", "precision": 10, "scale": 2},
    "岗位工资": {"target_field": "position_salary", "data_type": "DECIMAL", "precision": 10, "scale": 2},
    "绩效工资": {"target_field": "performance_salary", "data_type": "DECIMAL", "precision": 10, "scale": 2},
    "工资": {"target_field": "salary", "data_type": "DECIMAL", "precision": 10, "scale": 2},
    
    # 政治面貌
    "政治面貌": {"target_field": "political_status", "data_type": "VARCHAR", "length": 20},
    "党员": {"target_field": "is_party_member", "data_type": "BOOLEAN"},
    "入党日期": {"target_field": "party_date", "data_type": "DATE"},
    
    # 其他常用字段
    "备注": {"target_field": "remark", "data_type": "TEXT"},
    "状态": {"target_field": "status", "data_type": "VARCHAR", "length": 20},
    "编号": {"target_field": "code", "data_type": "VARCHAR", "length": 30},
    "序号": {"target_field": "seq_no", "data_type": "INTEGER"},
}

# 数据类型推断规则
DATA_TYPE_RULES = {
    "INTEGER": {
        "patterns": [r'^\d+$'],
        "examples": ['123', '0', '9999']
    },
    "DECIMAL": {
        "patterns": [r'^\d+\.\d+$'],
        "examples": ['123.45', '0.00', '9999.99']
    },
    "DATE": {
        "patterns": [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{4}/\d{2}/\d{2}$',
            r'^\d{4}年\d{2}月\d{2}日$'
        ],
        "examples": ['2023-01-15', '2023/01/15', '2023年01月15日']
    },
    "BOOLEAN": {
        "patterns": [r'^(是|否|true|false|1|0|yes|no)$'],
        "examples": ['是', '否', 'true', 'false']
    }
}


def infer_data_type(values: List[Any]) -> Dict[str, Any]:
    """根据数据样本推断数据类型"""
    # 过滤空值
    non_null_values = [str(v) for v in values if pd.notna(v) and str(v).strip()]
    
    if not non_null_values:
        return {"data_type": "VARCHAR", "length": 255}
    
    # 检查是否匹配特定类型规则
    import re
    
    for data_type, rules in DATA_TYPE_RULES.items():
        match_count = 0
        for value in non_null_values:
            for pattern in rules["patterns"]:
                if re.match(pattern, str(value), re.IGNORECASE):
                    match_count += 1
                    break
        
        # 如果80%以上的数据匹配该类型，则使用该类型
        if match_count / len(non_null_values) >= 0.8:
            if data_type == "INTEGER":
                return {"data_type": "INTEGER"}
            elif data_type == "DECIMAL":
                return {"data_type": "DECIMAL", "precision": 10, "scale": 2}
            elif data_type == "DATE":
                return {"data_type": "DATE"}
            elif data_type == "BOOLEAN":
                return {"data_type": "BOOLEAN"}
    
    # 默认为VARCHAR，根据内容长度确定
    max_length = max(len(str(v)) for v in non_null_values)
    # 向上取整到标准长度
    if max_length <= 10:
        length = 10
    elif max_length <= 20:
        length = 20
    elif max_length <= 50:
        length = 50
    elif max_length <= 100:
        length = 100
    elif max_length <= 200:
        length = 200
    else:
        length = 500
    
    return {"data_type": "VARCHAR", "length": length}


def generate_smart_mapping(field_name: str, values: List[Any]) -> Dict[str, Any]:
    """生成智能字段映射建议"""
    # 清理字段名
    clean_field = field_name.strip()
    
    # 首先尝试精确匹配规则库
    if clean_field in FIELD_MAPPING_RULES:
        mapping = FIELD_MAPPING_RULES[clean_field].copy()
        mapping["source_field"] = field_name
        mapping["confidence"] = "high"
        mapping["relation_type"] = "none"
        mapping["relation_table"] = ""
        mapping["relation_display_field"] = "name"
        return mapping
    
    # 尝试部分匹配
    for cn_name, mapping_rule in FIELD_MAPPING_RULES.items():
        if cn_name in clean_field or clean_field in cn_name:
            mapping = mapping_rule.copy()
            mapping["source_field"] = field_name
            mapping["confidence"] = "medium"
            mapping["relation_type"] = "none"
            mapping["relation_table"] = ""
            mapping["relation_display_field"] = "name"
            return mapping
    
    # 如果没有匹配到规则，根据数据内容推断类型
    inferred = infer_data_type(values)
    
    # 生成英文字段名（使用下划线替换空格）
    import re
    # 移除特殊字符，替换空格为下划线
    target_field = re.sub(r'[^\w\s]', '', clean_field)
    target_field = re.sub(r'\s+', '_', target_field).lower()
    
    # 如果转换后为空，使用默认名称
    if not target_field:
        target_field = f"field_{hash(field_name) % 10000}"
    
    return {
        "source_field": field_name,
        "target_field": target_field,
        "confidence": "low",
        "relation_type": "none",
        "relation_table": "",
        "relation_display_field": "name",
        **inferred
    }


@router.post("/parse-file")
async def parse_file(file: UploadFile = File(...)):
    """解析上传的文件并生成智能映射建议"""
    try:
        # 检查文件类型
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="只支持Excel和CSV文件")
        
        # 读取文件内容
        contents = await file.read()
        
        # 根据文件类型解析
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # 获取原始字段列表
        original_fields = df.columns.tolist()
        
        # 生成智能映射建议
        suggested_mappings = []
        for field in original_fields:
            values = df[field].tolist()
            mapping = generate_smart_mapping(field, values)
            suggested_mappings.append(mapping)
        
        # 获取前10行数据作为预览
        preview_data = df.head(10).to_dict(orient='records')
        
        # 转换预览数据中的NaN为None
        for row in preview_data:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None
        
        # 判断表类型
        table_type = "master"
        lower_filename = file.filename.lower()
        if any(keyword in lower_filename for keyword in ["字典", "类型", "层次", "dict", "type", "level"]):
            table_type = "dictionary"
            print(f"根据文件名 '{file.filename}' 自动识别为字典表")
        
        return {
            "fields": original_fields,
            "preview_data": preview_data,
            "total_rows": len(df),
            "filename": file.filename,
            "table_type": table_type,
            "suggested_mappings": suggested_mappings
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")
