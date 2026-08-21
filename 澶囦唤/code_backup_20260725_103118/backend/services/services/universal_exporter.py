"""
通用导出器 - 实现核心功能
上传模板 → 识别占位符 → 填充数据 → 导出文件（100%保留原格式）
"""
import os
import shutil
import tempfile
from docx import Document
from openpyxl import load_workbook


def export_word(template_path: str, data: dict) -> str:
    """导出Word文件 - 复制模板，替换{{字段名}}"""
    # 生成输出路径
    output_path = os.path.join(tempfile.gettempdir(), os.path.basename(template