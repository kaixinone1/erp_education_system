#!/usr/bin/env python3
"""
通用模板处理器
自动识别表格结构并生成占位符
"""
import re
import os
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup


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


def is_likely_label(text: str) -> bool:
    """判断文本是否可能是字段标签"""
    text = text.strip()
    if not text:
        return False
    # 常见标签列表
    common_labels = [
        '姓名', '性别', '出生日期', '民族', '文化程度', '身份证号码',
        '岗位', '职务', '薪级', '参加工作时间', '工作年限',
        '籍贯', '现住址', '退休原因', '退休时间',
        '事业管理岗位', '事业专技岗位', '事业工勤岗位',
        '对应原职务', '对应技术等级',
        '入党年月', '技术职称', '是否独生子女',
        '自何年何月', '至何年何月', '所在单位及职务',
        '证明人及住址', '直系亲属供养情况