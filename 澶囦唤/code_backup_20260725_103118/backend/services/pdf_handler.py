"""
PDF处理服务 - PDF转图片、坐标标记（支持多页）
"""
import os
from typing import Dict, Any, List, Optional, Tuple
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Poppler路径（Windows）
POPPLER_PATH = r'd:\erp_thirteen\tools\poppler-24.08.0\Library\bin'


class PDFHandler:
    """PDF处理器"""
    
    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """
        获取PDF总页数
        """
        from pdf2image.pdf2image import pdfinfo_from_path
        info = pdfinfo_from_path(pdf_path, poppler_path=POPPLER_PATH)
        return int(info.get('Pages', 1))
    
    @staticmethod
    def pdf_page_to_image(pdf_path: str, page: int = 1, dpi: int = 150) -> str:
        """
        将PDF指定页转换为图片（base64）
        
        Args:
            pdf_path: PDF文件路径
            page: 页码（从1开始）
            dpi: 分辨率
            
        Returns:
            base64编码的图片字符串
        """
        # 转换PDF为图片
        images = convert_from_path(
            pdf_path, 
            dpi=dpi, 
            first_page=page, 
            last_page=page,
            poppler_path=POPPLER_PATH
        )
        
        if not images:
            raise ValueError("PDF转换失败")
        
        img = images[0]
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def get_image_dimensions(pdf_path: str, page: int = 1, dpi: int = 150) -> Tuple[int, int]:
        """
        获取PDF指定页转换后的图片尺寸
        
        Returns:
            (width, height)
        """
        images = convert_from_path(
            pdf_path, 
            dpi=dpi, 
            first_page=page, 
            last_page=page,
            poppler_path=POPPLER_PATH
        )
        if not images:
            raise ValueError("PDF转换失败")
        
        img = images[0]
        return img.size

    @staticmethod
    def generate_preview_with_marks(
        pdf_path: str,
        marks: List[Dict],
        selected_mark: Optional[Dict] = None,
        page: int = 1,
        dpi: int = 150
    ) -> str:
        """
        生成带标记的预览图
        
        Args:
            pdf_path: PDF文件路径
            marks: 标记列表 [{x, y, page, label, field_name}]
            selected_mark: 当前选中的标记
            page: 当前页码
            dpi: 分辨率
            
        Returns:
            base64编码的图片字符串
        """
        # 转换PDF为图片
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            first_page=page,
            last_page=page,
            poppler_path=POPPLER_PATH
        )
        if not images:
            raise ValueError("PDF转换失败")
        
        img = images[0].convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            font = ImageFont.truetype("simhei.ttf", 14)
            small_font = ImageFont.truetype("simhei.ttf", 12)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 14)
                small_font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
                small_font = font
        
        # 获取图片尺寸
        img_width, img_height = img.size
        
        # 获取PDF页面尺寸（用于坐标转换）
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            pdf_page = pdf.pages[page - 1]
            pdf_width_pt = pdf_page.width
            pdf_height_pt = pdf_page.height
        
        # 计算缩放比例（使用统一的缩放比例）
        scale = img_width / pdf_width_pt
        
        # 过滤当前页的标记
        page_marks = [m for m in marks if m.get('page', 1) == page]
        
        # 绘制所有标记
        for i, mark in enumerate(page_marks):
            # PDF坐标转换为图片坐标
            pdf_x = mark.get('x', 0)
            pdf_y = mark.get('y', 0)
            
            # 缩放坐标（使用统一缩放比例）
            x = pdf_x * scale
            # pdfplumber的Y坐标从顶部开始，与图片坐标一致，不需要翻转
            y = pdf_y * scale
            
            label = mark.get('label', f'字段{i+1}')
            
            # 判断是否选中
            is_selected = selected_mark and selected_mark.get('x') == x and selected_mark.get('y') == y
            
            # 标记点大小
            size = 12 if is_selected else 8
            
            # 颜色
            if is_selected:
                color = '#f56c6c'  # 红色 - 选中
                text_color = '#f56c6c'
            else:
                color = '#1890ff'  # 蓝色 - 普通
                text_color = '#1890ff'
            
            # 绘制圆点
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color, outline='white', width=2)
            
            # 绘制标签背景
            bbox = draw.textbbox((0, 0), label, font=small_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            label_x = x + size + 4
            label_y = y - text_height // 2
            
            # 标签背景
            draw.rectangle(
                [label_x - 2, label_y - 2, label_x + text_width + 4, label_y + text_height + 2],
                fill='white',
                outline=color,
                width=1
            )
            
            # 绘制标签文字
            draw.text((label_x, label_y), label, fill=text_color, font=small_font)
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"


# 便捷函数
def pdf_page_to_image(pdf_path: str, page: int = 1, dpi: int = 150) -> str:
    """PDF指定页转图片便捷函数"""
    return PDFHandler.pdf_page_to_image(pdf_path, page, dpi)


def generate_preview_with_marks(pdf_path: str, marks: List[Dict], selected_mark: Optional[Dict] = None, page: int = 1, dpi: int = 150) -> str:
    """生成带标记预览图便捷函数"""
    return PDFHandler.generate_preview_with_marks(pdf_path, marks, selected_mark, page, dpi)


def get_pdf_page_count(pdf_path: str) -> int:
    """获取PDF总页数便捷函数"""
    return PDFHandler.get_page_count(pdf_path)
