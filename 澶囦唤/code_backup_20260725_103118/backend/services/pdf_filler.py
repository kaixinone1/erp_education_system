"""
PDF填充服务
用于将数据填充到模板中并生成可打印的HTML
"""
import os
import tempfile
from typing import Dict, Optional


class PDFFiller:
    """PDF填充器"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def fill_template(self, template_path: str, data: Dict, template_id: str, teacher_id: str, 
                      page_settings: Dict = None) -> Optional[str]:
        """
        填充模板并生成可打印的HTML
        
        Args:
            template_path: 原始模板路径
            data: 填充数据 {字段名: 值}
            template_id: 模板ID
            teacher_id: 教师ID
            page_settings: 页面设置 {paper_size, is_landscape, margin}
            
        Returns:
            生成的HTML文件路径
        """
        try:
            # 判断文件类型
            file_ext = os.path.splitext(template_path)[1].lower()
            
            if file_ext in ['.html', '.htm']:
                # HTML模板
                return self._fill_html_template(template_path, data, template_id, teacher_id, page_settings)
            else:
                print(f"不支持的文件格式: {file_ext}")
                return None
            
        except Exception as e:
            print(f"填充模板失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _fill_html_template(self, template_path: str, data: Dict, template_id: str, teacher_id: str,
                           page_settings: Dict = None) -> Optional[str]:
        """填充HTML模板并生成可打印的HTML"""
        try:
            # 读取HTML文件（尝试多种编码）
            html_content = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    with open(template_path, 'r', encoding=encoding) as f:
                        html_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if html_content is None:
                raise Exception("无法读取文件，编码不支持")
            
            # 填充数据（替换占位符）
            for field_name, value in data.items():
                if value is not None:
                    placeholder = f"{{{{{field_name}}}}}"
                    html_content = html_content.replace(placeholder, str(value))
            
            # 获取页面设置
            paper_size = 'A4'
            is_landscape = False
            if page_settings:
                paper_size = page_settings.get('paper_size', 'A4')
                is_landscape = page_settings.get('is_landscape', False)
            
            # 构建打印样式
            page_size = f"{paper_size} landscape" if is_landscape else paper_size
            
            print_styles = f"""
            <style>
                @page {{
                    size: {page_size};
                    margin: 10mm;
                }}
                @media print {{
                    body {{ margin: 0; }}
                    .no-print {{ display: none !important; }}
                }}
                body {{
                    font-family: "SimSun", "宋体", "Microsoft YaHei", serif;
                    margin: 20px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                td, th {{
                    border: 1px solid #000;
                    padding: 8px;
                }}
            </style>
            """
            
            # 构建完整的HTML文档
            charset_meta = '<meta charset="UTF-8">'
            
            if '<!DOCTYPE html>' not in html_content and '<html' not in html_content:
                # 简单的HTML内容，包装成完整文档
                full_html = f"""<!DOCTYPE html>
<html>
<head>
    {charset_meta}
    <title>报表 - {teacher_id}</title>
    {print_styles}
</head>
<body>
    {html_content}
</body>
</html>"""
            elif '<head>' in html_content:
                # 已有完整HTML结构，插入编码和样式
                full_html = html_content.replace('<head>', f'<head>\n    {charset_meta}\n    {print_styles}')
                # 移除旧的gb2312编码声明
                full_html = full_html.replace('charset=gb2312', 'charset=UTF-8')
            else:
                full_html = html_content
            
            # 添加打印按钮
            print_button = """
            <div class="no-print" style="position: fixed; top: 10px; right: 10px; z-index: 9999; 
                                         background: #f0f0f0; padding: 10px; border-radius: 4px; 
                                         box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                <button onclick="window.print()" style="padding: 8px 16px; font-size: 14px; cursor: pointer;">
                    🖨️ 打印 / 另存为PDF
                </button>
                <span style="margin-left: 10px; color: #666; font-size: 12px;">
                    (选择"另存为PDF"作为打印机)
                </span>
            </div>
            """
            
            # 在body开头插入打印按钮
            if '<body>' in full_html:
                full_html = full_html.replace('<body>', f'<body>\n    {print_button}')
            
            # 保存输出文件
            output_filename = f"{template_id}_{teacher_id}_print.html"
            output_path = os.path.join(self.temp_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            return output_path
            
        except Exception as e:
            print(f"填充HTML模板失败: {e}")
            import traceback
            traceback.print_exc()
            return None
