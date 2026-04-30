"""
A3纸四区域检测服务 - 双面2栏格式
用于检测A3对折小册子格式的4个编辑区域

格式说明：
- A3纸张，双面打印
- 每面2栏，每栏44.6字符
- 第1页（正面）：区域1（左栏）、区域2（右栏）
- 第2页（背面）：区域3（左栏）、区域4（右栏）
"""
import pdfplumber
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Region:
    """编辑区域"""
    id: int  # 区域编号 1-4
    name: str  # 区域名称
    page: int  # 所在页码 1-2
    x0: float  # 左边界
    y0: float  # 上边界
    x1: float  # 右边界
    y1: float  # 下边界
    corners: List[Tuple[float, float]]  # 四角坐标 [(左上), (右上), (左下), (右下)]
    adjusted: bool = False  # 是否手动调整过


class A3RegionDetector:
    """A3纸四区域检测器 - 双面2栏格式"""
    
    # A3纸标准尺寸 (pt, 1pt = 1/72 inch)
    A3_WIDTH_PT = 1190.55  # 420mm
    A3_HEIGHT_PT = 841.89  # 297mm
    
    # 页边距 (3cm ≈ 85pt)
    MARGIN_PT = 85
    
    # 装订线宽度 (约7mm ≈ 20pt)
    BINDING_SPACE_PT = 20
    
    # 栏宽（44.6字符，按11.22pt/字符计算）
    COL_WIDTH_PT = 500.275  # (1190.55 - 85*2 - 20) / 2
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
    
    def detect_regions(self, page_num: int = 1) -> Optional[List[Region]]:
        """
        检测指定页面的2个编辑区域
        
        Args:
            page_num: 页码，1=正面（区域1、2），2=背面（区域3、4）
            
        Returns:
            2个区域的列表，如果不是A3格式返回None
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            if page_num > len(pdf.pages):
                return None
            
            page = pdf.pages[page_num - 1]
            page_width = page.width
            page_height = page.height
            
            # 检测是否为A3格式（宽度大于800pt）
            if page_width < 800:
                return None
            
            # 计算区域边界
            return self._calculate_regions(page_width, page_height, page_num)
    
    def _calculate_regions(self, page_width: float, page_height: float, page_num: int) -> List[Region]:
        """
        计算2个区域的边界
        
        区域编号规则：
        - 第1页（正面）：区域1（左栏）、区域2（右栏）
        - 第2页（背面）：区域3（左栏）、区域4（右栏）
        
        坐标计算：
        - 页边距：85pt
        - 装订线：20pt
        - 栏宽：500.275pt（44.6字符）
        """
        margin = self.MARGIN_PT
        binding = self.BINDING_SPACE_PT
        col_width = self.COL_WIDTH_PT
        
        # 计算栏的X坐标
        left_col_x0 = margin
        left_col_x1 = margin + col_width
        right_col_x0 = left_col_x1 + binding
        right_col_x1 = right_col_x0 + col_width
        
        # Y坐标（上下页边距）
        y0 = margin
        y1 = page_height - margin
        
        regions = []
        
        if page_num == 1:
            # 第1页（正面）：区域1、区域2
            
            # 区域1：左栏（正面）
            region1 = Region(
                id=1,
                name="区域1（左栏-正面）",
                page=1,
                x0=left_col_x0,
                y0=y0,
                x1=left_col_x1,
                y1=y1,
                corners=[
                    (left_col_x0, y0),  # 左上
                    (left_col_x1, y0),  # 右上
                    (left_col_x0, y1),  # 左下
                    (left_col_x1, y1)   # 右下
                ]
            )
            regions.append(region1)
            
            # 区域2：右栏（正面）
            region2 = Region(
                id=2,
                name="区域2（右栏-正面）",
                page=1,
                x0=right_col_x0,
                y0=y0,
                x1=right_col_x1,
                y1=y1,
                corners=[
                    (right_col_x0, y0),  # 左上
                    (right_col_x1, y0),  # 右上
                    (right_col_x0, y1),  # 左下
                    (right_col_x1, y1)   # 右下
                ]
            )
            regions.append(region2)
            
        else:
            # 第2页（背面）：区域3、区域4
            
            # 区域3：左栏（背面）
            region3 = Region(
                id=3,
                name="区域3（左栏-背面）",
                page=2,
                x0=left_col_x0,
                y0=y0,
                x1=left_col_x1,
                y1=y1,
                corners=[
                    (left_col_x0, y0),  # 左上
                    (left_col_x1, y0),  # 右上
                    (left_col_x0, y1),  # 左下
                    (left_col_x1, y1)   # 右下
                ]
            )
            regions.append(region3)
            
            # 区域4：右栏（背面）
            region4 = Region(
                id=4,
                name="区域4（右栏-背面）",
                page=2,
                x0=right_col_x0,
                y0=y0,
                x1=right_col_x1,
                y1=y1,
                corners=[
                    (right_col_x0, y0),  # 左上
                    (right_col_x1, y0),  # 右上
                    (right_col_x0, y1),  # 左下
                    (right_col_x1, y1)   # 右下
                ]
            )
            regions.append(region4)
        
        return regions
    
    def get_region_preview_data(self, page_num: int = 1) -> Optional[Dict]:
        """
        获取区域预览数据（用于前端显示）
        
        Returns:
            包含区域信息和四角坐标的字典
        """
        regions = self.detect_regions(page_num)
        if not regions:
            return None
        
        with pdfplumber.open(self.pdf_path) as pdf:
            page = pdf.pages[page_num - 1]
            page_width = page.width
            page_height = page.height
        
        return {
            "is_a3": True,
            "page": page_num,
            "page_width": page_width,
            "page_height": page_height,
            "regions": [
                {
                    "id": r.id,
                    "name": r.name,
                    "page": r.page,
                    "bounds": {
                        "x0": r.x0,
                        "y0": r.y0,
                        "x1": r.x1,
                        "y1": r.y1
                    },
                    "corners": [
                        {"x": c[0], "y": c[1], "position": pos}
                        for c, pos in zip(r.corners, ["左上", "右上", "左下", "右下"])
                    ],
                    "adjusted": r.adjusted
                }
                for r in regions
            ]
        }
    
    def extract_fields_from_region(self, region: Region, page_num: int = 1) -> List[Dict]:
        """
        从指定区域提取字段
        
        Args:
            region: 区域对象
            page_num: 页码
            
        Returns:
            字段列表
        """
        from .field_extractor import TableFieldExtractor
        
        with pdfplumber.open(self.pdf_path) as pdf:
            page = pdf.pages[page_num - 1]
            
            # 裁剪到指定区域
            cropped = page.crop((region.x0, region.y0, region.x1, region.y1))
            
            # 使用字段提取器提取字段
            extractor = TableFieldExtractor(self.pdf_path)
            words = cropped.extract_words()
            
            fields = []
            
            # 检测表格
            tables = cropped.find_tables()
            
            for table in tables:
                table_fields = extractor._extract_from_table(table, words, page_num)
                for field in table_fields:
                    # 调整坐标到原始页面坐标系
                    field.x += region.x0
                    field.y += region.y0
                    field_dict = {
                        "name": field.name,
                        "label": field.label,
                        "x": field.x,
                        "y": field.y,
                        "page": field.page,
                        "width": field.width,
                        "height": field.height,
                        "type": field.field_type,
                        "confidence": field.confidence,
                        "region_id": region.id
                    }
                    fields.append(field_dict)
            
            # 如果没有找到表格字段，尝试智能识别表单字段
            if not fields and words:
                fields = self._extract_form_fields(words, region, page_num)
            
            return fields
    
    def _extract_form_fields(self, words: List[Dict], region: Region, page_num: int) -> List[Dict]:
        """
        智能识别表单字段
        支持模式：
        1. "同意__同志" - 提取同意和同志之间的空白处（区域1）
        2. "姓名：" - 提取冒号后面的空白处（区域2）
        """
        fields = []
        field_index = 0
        
        # 找到所有"同意"和"同志"的位置
        agrees = [(i, w) for i, w in enumerate(words) if '同意' in w['text']]
        comrades = [(i, w) for i, w in enumerate(words) if '同志' in w['text']]
        
        # 模式1: 匹配同一行的"同意"和"同志"之间的空白
        for agree_idx, agree_word in agrees:
            for comrade_idx, comrade_word in comrades:
                # 检查是否在同一行（y坐标接近）
                y_diff = abs(comrade_word['top'] - agree_word['top'])
                if y_diff < 10:  # 同一行
                    # 计算间距
                    x_gap = comrade_word['x0'] - agree_word['x1']
                    if x_gap > 10:  # 有空白
                        field_dict = {
                            "name": f"name_field_{field_index}",
                            "label": f"姓名_{field_index+1}",
                            "x": agree_word['x1'] + region.x0,
                            "y": agree_word['top'] + region.y0,
                            "page": page_num,
                            "width": x_gap,
                            "height": agree_word['bottom'] - agree_word['top'],
                            "type": "text",
                            "confidence": 0.95,
                            "region_id": region.id
                        }
                        fields.append(field_dict)
                        field_index += 1
        
        # 模式2: 匹配"姓名："
        for i, word in enumerate(words):
            if '姓名' in word['text']:
                # 检查这个词或下一个词是否包含冒号
                has_colon = '：' in word['text'] or ':' in word['text']
                colon_word = word
                
                if not has_colon and i + 1 < len(words):
                    next_word = words[i + 1]
                    if '：' in next_word['text'] or ':' in next_word['text']:
                        has_colon = True
                        colon_word = next_word
                
                if has_colon:
                    # 在区域2（右栏）中，姓名后面应该有空白
                    # 默认创建一个标准宽度的字段
                    field_dict = {
                        "name": f"name_field_{field_index}",
                        "label": "姓名",
                        "x": colon_word['x1'] + region.x0,
                        "y": colon_word['top'] + region.y0,
                        "page": page_num,
                        "width": 100,  # 默认宽度100pt
                        "height": colon_word['bottom'] - colon_word['top'],
                        "type": "text",
                        "confidence": 0.8,
                        "region_id": region.id
                    }
                    fields.append(field_dict)
                    field_index += 1
        
        return fields


def detect_a3_regions(pdf_path: str, page_num: int = 1) -> Optional[List[Dict]]:
    """
    便捷函数：检测A3纸的2个区域（指定页）
    
    Args:
        pdf_path: PDF文件路径
        page_num: 页码，1=正面（区域1、2），2=背面（区域3、4）
        
    Returns:
        区域列表，每个区域包含边界和四角坐标
    """
    detector = A3RegionDetector(pdf_path)
    preview_data = detector.get_region_preview_data(page_num)
    
    if not preview_data:
        return None
    
    return preview_data["regions"]
