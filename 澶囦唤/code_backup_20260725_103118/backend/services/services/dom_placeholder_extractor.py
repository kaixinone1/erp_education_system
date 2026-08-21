"""
基于DOM的占位符提取服务
只在HTML文本节点中查找占位符，避免CSS代码干扰
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


def extract_placeholders_from_text(text: str) -> List[str]:
    """从纯文本中提取占位符"""
    placeholders = []
    
    # 支持多种格式：{字段名}、{{字段名}}、[字段名]、[[字段名]]
    patterns = [
        r'\{\{([^{}]+)\}\}',  # {{字段名}}
        r'\[\[([^\[\]]+)\]\]',  # [[字段名]]
        r'\{([^{}]+)\}',       # {字段名}
        r'\[([^\[\]]+)\]',     # [字段名]
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            match = match.strip()
            # 简单验证：不为空，长度合理，包含中文或字母
            if match and len(match) < 50:
                if re.search(r'[\u4e00-\u9fa5a-zA-Z]', match):
                    placeholders.append(match)
    
    return placeholders


def extract_from_html(file_path: str) -> List[Dict[str, Any]]:
    """从HTML文件中提取占位符（使用DOM解析）"""
    fields = []
    
    try:
        content = read_file_with_encoding(file_path)
        soup = BeautifulSoup(content, 'html.parser')
        
        # 只在文本节点中查找占位符
        seen = set()
        for element in soup.find_all(text=True):
            text = str(element)
            placeholders = extract_placeholders_from_text(text)
            for ph in placeholders:
                if ph not in seen:
                    seen.add(ph)
                    fields.append({
                        'name': ph,
                        'label': ph,
                        'field_type': 'text',
                        'source': 'html_text'
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
        # 其他格式先读取文本内容再提取
        try:
            content = read_file_with_encoding(file_path)
            placeholders = extract_placeholders_from_text(content)
            return [{'name': ph, 'label': ph, 'field_type': 'text', 'source': 'text'} 
                    for ph in set(placeholders)]
        except Exception as e:
            print(f"提取字段失败: {e}")
            return []
