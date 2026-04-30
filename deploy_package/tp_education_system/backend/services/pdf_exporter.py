"""
PDF导出服务
使用Playwright将HTML转换为PDF
"""
import os
import tempfile
from typing import Dict, Optional


class PDFExporter:
    """PDF导出器"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def export_pdf(self, html_content: str, template_id: str, teacher_id: str,
                   page_settings: Dict = None) -> Optional[str]:
        """
        将HTML内容导出为PDF
        保留原始HTML的完整结构和样式
        
        Args:
            html_content: HTML内容（完整的HTML文档）
            template_id: 模板ID
            teacher_id: 教师ID
            page_settings: 页面设置
            
        Returns:
            PDF文件路径
        """
        try:
            from playwright.sync_api import sync_playwright
            
            # 获取页面设置
            paper_size = page_settings.get('paper_size', 'A4') if page_settings else 'A4'
            is_landscape = page_settings.get('is_landscape', False) if page_settings else False
            
            # 确保HTML内容包含完整的文档结构
            if '<!DOCTYPE html>' not in html_content and '<html' not in html_content:
                # 如果不是完整HTML，包装成完整文档
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>报表</title>
</head>
<body>
    {html_content}
</body>
</html>"""
            
            # 添加或更新打印样式
            print_style = f"""
            <style>
                @page {{
                    size: {paper_size} {'landscape' if is_landscape else 'portrait'};
                    margin: 5mm;
                }}
                @media print {{
                    body {{ margin: 0; padding: 0; }}
                }}
            </style>
            </head>
            """
            
            # 在</head>前插入打印样式
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', print_style)
            else:
                # 如果没有head标签，在<body>前添加
                html_content = html_content.replace('<body', f'<head>{print_style}</head><body')
            
            # 保存HTML到临时文件
            html_filename = f"{template_id}_{teacher_id}_temp.html"
            html_path = os.path.join(self.temp_dir, html_filename)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 使用Playwright生成PDF
            output_filename = f"{template_id}_{teacher_id}_报表.pdf"
            output_path = os.path.join(self.temp_dir, output_filename)
            
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # 加载HTML文件
                page.goto(f'file:///{html_path}')
                
                # 等待页面加载完成
                page.wait_for_load_state('networkidle')
                
                # 生成PDF - 使用原始页面尺寸
                page.pdf(
                    path=output_path,
                    format=paper_size,
                    landscape=is_landscape,
                    margin={
                        'top': '5mm',
                        'right': '5mm',
                        'bottom': '5mm',
                        'left': '5mm'
                    },
                    print_background=True
                )
                
                browser.close()
            
            # 删除临时HTML文件
            if os.path.exists(html_path):
                os.remove(html_path)
            
            return output_path
            
        except Exception as e:
            print(f"导出PDF失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def export_from_template(self, template_path: str, data: Dict, template_id: str, 
                            teacher_id: str, page_settings: Dict = None) -> Optional[str]:
        """
        从模板文件导出PDF
        
        Args:
            template_path: 模板文件路径
            data: 填充数据
            template_id: 模板ID
            teacher_id: 教师ID
            page_settings: 页面设置
            
        Returns:
            PDF文件路径
        """
        try:
            # 读取模板文件
            html_content = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    with open(template_path, 'r', encoding=encoding) as f:
                        html_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if html_content is None:
                raise Exception("无法读取模板文件")
            
            # 填充数据
            for field_name, value in data.items():
                if value is not None:
                    placeholder = f"{{{{{field_name}}}}}"
                    html_content = html_content.replace(placeholder, str(value))
            
            # 导出PDF
            return self.export_pdf(html_content, template_id, teacher_id, page_settings)
            
        except Exception as e:
            print(f"从模板导出PDF失败: {e}")
            import traceback
            traceback.print_exc()
            return None
