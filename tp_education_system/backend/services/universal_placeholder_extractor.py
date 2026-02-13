"""
通用占位符提取服务
支持双花括号格式 {{字段名}}，避免与CSS代码冲突
"""
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any


def read_file_with_encoding(file_path: str) -> str:
    """尝试多种编码读取文件"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(file_path, 'r', encoding='latin-1') as f:
        return f.read()


def clean_html_tags(text: str) -> str:
    """去除HTML标签"""
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 去除HTML实体
    text = re.sub(r'&[^;]+;', '', text)
    # 去除多余空白
    text = ' '.join(text.split())
    return text


def extract_placeholders(text: str) -> List[str]:
    """从文本中提取占位符，支持双花括号 {{字段名}} 和单花括号 {字段名}"""
    placeholders = []
    
    # 先清理HTML标签
    cleaned_text = clean_html_tags(text)
    
    # 匹配双花括号格式 {{字段名}}
    pattern_double = r'\{\{([^{}]+)\}\}'
    matches_double = re.findall(pattern_double, cleaned_text)
    
    for match in matches_double:
        match = match.strip()
        # 简单验证：不为空，长度合理，包含中文或字母
        if match and 0 < len(match) < 50:
            if re.search(r'[\u4e00-\u9fa5a-zA-Z]', match):
                placeholders.append(match)
    
    # 匹配单花括号格式 {字段名}
    pattern_single = r'\{([^{}]+)\}'
    matches_single = re.findall(pattern_single, cleaned_text)
    
    for match in matches_single:
        match = match.strip()
        # 简单验证：不为空，长度合理，包含中文或字母
        if match and 0 < len(match) < 50:
            if re.search(r'[\u4e00-\u9fa5a-zA-Z]', match):
                placeholders.append(match)
    
    return placeholders


def extract_from_html(file_path: str) -> List[Dict[str, Any]]:
    """从HTML文件中提取占位符"""
    fields = []
    
    try:
        content = read_file_with_encoding(file_path)
        
        # 先在整个内容中提取（处理{{和}}被标签分割的情况）
        placeholders = extract_placeholders(content)
        
        seen = set()
        for ph in placeholders:
            if ph not in seen:
                seen.add(ph)
                fields.append({
                    'name': ph,
                    'label': ph,
                    'field_type': 'text',
                    'source': 'html'
                })
        
    except Exception as e:
        print(f"提取HTML字段失败: {e}")
    
    return fields


def extract_fields(file_path: str, file_ext: str) -> List[Dict[str, Any]]:
    """通用字段提取入口"""
    ext = file_ext.lower()
    
    if ext in ['.html', '.htm']:
        return extract_from_html(file_path)
    else:
        try:
            content = read_file_with_encoding(file_path)
            placeholders = extract_placeholders(content)
            return [{'name': ph, 'label': ph, 'field_type': 'text', 'source': 'text'} 
                    for ph in set(placeholders)]
        except Exception as e:
            print(f"提取字段失败: {e}")
            return []
