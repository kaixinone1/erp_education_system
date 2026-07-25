"""
PDF字段自动提取服务 - V2版本
针对复杂表格结构优化，精准定位到输入框
"""
import pdfplumber
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExtractedField:
    """提取的字段"""
    name: str
    label: str
    x: float
    y: float
    page: int
    width: float = 0
    height: float = 0
    field_type: str = "text"
    confidence: float = 1.0


class TableFieldExtractor:
    """表格字段提取器 - 专门处理表格型表单"""
    
    # 常见表单字段关键词
    FIELD_KEYWORDS = [
        "姓名", "性别", "出生", "年月", "年龄", "民族", "籍贯", "政治面貌",
        "学历", "学位", "专业", "毕业", "学校", "院校", "身份证", "号码",
        "电话", "手机", "邮箱", "地址", "单位", "职务", "职称", "岗位",
        "工作", "参加", "时间", "日期", "年限", "工龄", "教龄",
        "退休", "申报", "审批", "意见", "签名", "盖章",
        "工资", "津贴", "补贴", "绩效", "薪级", "级别"
    ]
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
    
    def extract_fields(self) -> List[ExtractedField]:
        """提取PDF中的所有字段"""
        fields = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_fields = self._extract_page_fields(page, page_num)
                fields.extend(page_fields)
        
        # 去重
        fields = self._deduplicate_fields(fields)
        # 按位置排序
        fields.sort(key=lambda f: (f.page, f.y, f.x))
        
        return fields
    
    def _extract_page_fields(self, page, page_num: int) -> List[ExtractedField]:
        """提取单页的字段"""
        fields = []
        words = page.extract_words()
        
        # 查找所有表格
        tables = page.find_tables()
        
        if tables:
            # 使用表格提取
            for table in tables:
                table_fields = self._extract_from_table(table, words, page_num)
                fields.extend(table_fields)
        else:
            # 非表格布局，使用传统方法
            fields = self._extract_non_table(page, words, page_num)
        
        return fields
    
    def _extract_from_table(self, table, words: List[Dict], page_num: int) -> List[ExtractedField]:
        """从表格中提取字段"""
        fields = []
        
        # 获取表格的所有行
        rows = table.rows
        
        for row_idx, row in enumerate(rows):
            cells = row.cells
            if not cells or len(cells) < 2:
                continue
            
            # 遍历单元格对（标签-值）
            i = 0
            while i < len(cells) - 1:
                label_cell = cells[i]
                value_cell = cells[i + 1]
                
                if not label_cell or not value_cell:
                    i += 1
                    continue
                
                # 获取标签单元格的文字
                label_text = self._get_cell_text(label_cell, words)
                
                # 检查是否是标签
                if self._is_label(label_text):
                    # 在值单元格中心放置标记
                    vx0, vy0, vx1, vy1 = value_cell
                    
                    field = ExtractedField(
                        name=self._normalize_field_name(label_text),
                        label=label_text,
                        x=(vx0 + vx1) / 2,
                        y=(vy0 + vy1) / 2,
                        page=page_num,
                        width=vx1 - vx0,
                        height=vy1 - vy0,
                        field_type=self._detect_field_type(label_text),
                        confidence=0.95
                    )
                    fields.append(field)
                    i += 2  # 跳过已处理的单元格对
                else:
                    i += 1
        
        return fields
    
    def _get_cell_text(self, cell_bbox: Tuple, words: List[Dict]) -> str:
        """获取单元格内的文字"""
        x0, y0, x1, y1 = cell_bbox
        cell_words = []
        
        for word in words:
            word_x = (word['x0'] + word['x1']) / 2
            word_y = (word['top'] + word['bottom']) / 2
            
            # 检查文字是否在单元格内（留一些边距）
            if x0 - 2 <= word_x <= x1 + 2 and y0 - 2 <= word_y <= y1 + 2:
                cell_words.append(word['text'])
        
        return ''.join(cell_words)
    
    def _is_label(self, text: str) -> bool:
        """判断是否是标签文本"""
        if not text:
            return False
        
        for keyword in self.FIELD_KEYWORDS:
            if keyword in text:
                return True
        
        return False
    
    def _normalize_field_name(self, text: str) -> str:
        """标准化字段名"""
        # 移除冒号和空格
        name = re.sub(r'[：:\s]+$', '', text)
        # 移除括号内容
        name = re.sub(r'[（(].*?[）)]', '', name)
        return name.strip()
    
    def _detect_field_type(self, text: str) -> str:
        """检测字段类型"""
        patterns = {
            "date": [r"日期", r"时间", r"年月", r"出生", r"工作"],
            "number": [r"工资", r"金额", r"补贴", r"年限", r"工龄", r"年龄", r"薪级"],
            "id_card": [r"身份证"],
            "phone": [r"电话", r"手机"],
            "select": [r"性别", r"民族", r"政治面貌", r"学历", r"学位"]
        }
        
        for field_type, pats in patterns.items():
            for pattern in pats:
                if re.search(pattern, text):
                    return field_type
        return "text"
    
    def _extract_non_table(self, page, words: List[Dict], page_num: int) -> List[ExtractedField]:
        """非表格布局的字段提取"""
        fields = []
        
        # 按y坐标分组（同一行）
        rows = self._group_by_rows(words)
        
        for row in rows:
            row.sort(key=lambda w: w['x0'])
            
            for i, word in enumerate(row):
                text = word['text']
                if self._is_label(text):
                    # 查找右侧的空白区域
                    right_x = word['x1']
                    if i + 1 < len(row):
                        next_x = row[i + 1]['x0']
                        gap = next_x - right_x
                    else:
                        gap = 100  # 默认宽度
                    
                    if gap > 20:
                        field = ExtractedField(
                            name=self._normalize_field_name(text),
                            label=text,
                            x=right_x + gap / 2,
                            y=(word['top'] + word['bottom']) / 2,
                            page=page_num,
                            width=gap,
                            height=word['bottom'] - word['top'],
                            field_type=self._detect_field_type(text),
                            confidence=0.8
                        )
                        fields.append(field)
        
        return fields
    
    def _group_by_rows(self, words: List[Dict], y_threshold: float = 5) -> List[List[Dict]]:
        """按y坐标分组"""
        if not words:
            return []
        
        sorted_words = sorted(words, key=lambda w: w['top'])
        rows = []
        current_row = [sorted_words[0]]
        
        for word in sorted_words[1:]:
            if abs(word['top'] - current_row[0]['top']) <= y_threshold:
                current_row.append(word)
            else:
                rows.append(current_row)
                current_row = [word]
        
        if current_row:
            rows.append(current_row)
        
        return rows
    
    def _deduplicate_fields(self, fields: List[ExtractedField]) -> List[ExtractedField]:
        """去重"""
        unique = []
        seen = set()
        
        for field in fields:
            # 按位置和名称去重
            key = (field.page, round(field.x / 30), round(field.y / 30), field.name)
            if key not in seen:
                seen.add(key)
                unique.append(field)
        
        return unique


def extract_pdf_fields(pdf_path: str) -> List[Dict]:
    """便捷函数"""
    extractor = TableFieldExtractor(pdf_path)
    fields = extractor.extract_fields()
    return [
        {
            "name": f.name,
            "label": f.label,
            "x": f.x,
            "y": f.y,
            "page": f.page,
            "width": f.width,
            "height": f.height,
            "type": f.field_type,
            "confidence": f.confidence
        }
        for f in fields
    ]
