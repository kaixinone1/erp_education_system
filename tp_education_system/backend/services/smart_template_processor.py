"""
智能模板处理器
自动分析HTML表格结构，识别标签和值区域，生成字段映射
"""
import re
import os
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup


def read_file_with_encoding(file_path: str) -> str:
    """尝试多种编码读取文件"""
    encodings = ['utf-8', 'gbk', 'gb2312',