"""
通用模板处理服务 - 一个引擎处理所有模板
实现100%格式复制：原模板 == 预览 == 导出
"""
import os
import json
import copy
import hashlib
from datetime import datetime
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font, Border, Side, PatternFill
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


class UniversalTemplateEngine:
    """通用模板处理引擎 - 实现100%格式复制"""
    
    def import_template(self, excel_path, template_name, template_type):
        """
        导入Excel模板，生成完整JSON配置（包含所有元数据）
        
        参数:
            excel_path: Excel文件路径
            template_name: 模板名称（如：职工退休呈报表）
            template_type: 模板类型（如：呈报表、审批表、公文）
        
        返回:
            JSON配置字典（包含完整元数据）
        """
        wb = load_workbook(excel_path, read_only=False, keep_links=False)
        ws = wb.active
        
        config = {
            "模板ID": self._generate_template_id(template_name),
            "模板名称": template_name,
            "模板类型": template_type,
            "原始文件": os.path.basename(excel_path),
            "原始文件路径": excel_path,
            "导入时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "页面设置": self._extract_page_setup(ws),
            "页边距": self._extract_page_margins(ws),
            "列宽": self._extract_column_widths(ws),
            "行高": self._extract_row_heights(ws),
            "单元格数据": self._extract_all_cells(ws),
            "样式数据": self._extract_all_styles(ws),
            "行数据": self._extract_rows_data(ws),
            "合并单元格": self._extract_merged_cells(ws),
            "字段映射": {}
        }
        
        wb.close()
        return config
    
    def extract_full_metadata(self, excel_path):
        """
        提取Excel文件的完整元数据（用于Luckysheet预览）
        
        参数:
            excel_path: Excel文件路径
        
        返回:
            完整元数据字典
        """
        wb = load_workbook(excel_path, read_only=False, keep_links=False)
        ws = wb.active
        
        metadata = {
            'filename': os.path.basename(excel_path),
            'sheets': wb.sheetnames,
            'active_sheet': wb.sheetnames.index(ws.title),
            'cells': [],
            'styles': {},
            'dimensions': {
                'rows': {},
                'columns': {},
                'max_row': ws.max_row,
                'max_column': ws.max_column
            },
            'merged_cells': [],
            'page_setup': {},
            'page_margins': {}
        }
        
        for row in ws.iter_rows():
            for cell in row:
                if hasattr(cell, 'column_letter'):
                    cell_key = f"{cell.column_letter}{cell.row}"
                else:
                    cell_key = f"{get_column_letter(cell.column)}{cell.row}"
                
                if cell.value is not None:
                    metadata['cells'].append({
                        'r': cell.row - 1,
                        'c': cell.column - 1,
                        'v': {
                            'v': cell.value,
                            'm': str(cell.value),
                        }
                    })
                
                style = {}
                
                if cell.font:
                    font_color = str(cell.font.color.rgb) if cell.font.color and hasattr(cell.font.color, 'rgb') else None
                    style['font'] = {
                        'name': cell.font.name,
                        'size': cell.font.size,
                        'bold': cell.font.bold,
                        'italic': cell.font.italic,
                        'color': font_color,
                        'underline': cell.font.underline,
                        'strike': cell.font.strike
                    }
                
                if cell.fill and cell.fill.patternType:
                    fg_color = str(cell.fill.fgColor.rgb) if cell.fill.fgColor and hasattr(cell.fill.fgColor, 'rgb') else None
                    bg_color = str(cell.fill.bgColor.rgb) if cell.fill.bgColor and hasattr(cell.fill.bgColor, 'rgb') else None
                    style['fill'] = {
                        'patternType': cell.fill.patternType,
                        'fgColor': fg_color,
                        'bgColor': bg_color
                    }
                
                if cell.border:
                    style['border'] = {}
                    for side in ['left', 'right', 'top', 'bottom']:
                        side_obj = getattr(cell.border, side, None)
                        if side_obj and side_obj.style:
                            border_color = str(side_obj.color.rgb) if side_obj.color and hasattr(side_obj.color, 'rgb') and side_obj.color.rgb else None
                            style['border'][side] = {
                                'style': side_obj.style,
                                'color': border_color
                            }
                
                if cell.alignment:
                    style['alignment'] = {
                        'horizontal': cell.alignment.horizontal,
                        'vertical': cell.alignment.vertical,
                        'wrapText': cell.alignment.wrapText,
                        'textRotation': cell.alignment.textRotation
                    }
                
                if cell.number_format and cell.number_format != 'General':
                    style['numberFormat'] = cell.number_format
                
                if style:
                    metadata['styles'][cell_key] = style
        
        for row_idx in range(1, ws.max_row + 1):
            row_dim = ws.row_dimensions[row_idx]
            if row_dim and row_dim.height:
                metadata['dimensions']['rows'][row_idx] = row_dim.height
        
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            col_dim = ws.column_dimensions.get(col_letter)
            if col_dim and col_dim.width:
                metadata['dimensions']['columns'][col_letter] = col_dim.width
        
        if hasattr(ws, 'merged_cells') and ws.merged_cells:
            for merged_range in ws.merged_cells.ranges:
                metadata['merged_cells'].append({
                    'range': str(merged_range),
                    'r': merged_range.min_row - 1,
                    'c': merged_range.min_col - 1,
                    'rs': merged_range.max_row - merged_range.min_row + 1,
                    'cs': merged_range.max_col - merged_range.min_col + 1
                })
        
        if hasattr(ws, 'page_setup') and ws.page_setup:
            ps = ws.page_setup
            page_setup_data = {
                'paperSize': ps.paperSize,
                'orientation': ps.orientation
            }
            try:
                page_setup_data['fitToPage'] = ps.fitToPage
            except:
                pass
            try:
                page_setup_data['fitToWidth'] = ps.fitToWidth
            except:
                pass
            try:
                page_setup_data['fitToHeight'] = ps.fitToHeight
            except:
                pass
            metadata['page_setup'] = page_setup_data
        
        if hasattr(ws, 'page_margins') and ws.page_margins:
            pm = ws.page_margins
            metadata['page_margins'] = {
                'left': pm.left,
                'right': pm.right,
                'top': pm.top,
                'bottom': pm.bottom,
                'header': pm.header,
                'footer': pm.footer
            }
        
        wb.close()
        return metadata
    
    def _generate_template_id(self, template_name):
        """生成模板ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_obj = hashlib.md5(f"{template_name}{timestamp}".encode())
        return f"tpl_{hash_obj.hexdigest()[:8]}"
    
    def _extract_all_cells(self, ws):
        """提取所有单元格数据（包含完整值和显示值）"""
        cells = []
        for row in ws.iter_rows():
            for cell in row:
                val = cell.value
                cells.append({
                    '行号': cell.row,
                    '列号': cell.column,
                    '值': val,
                    '显示值': str(val) if val is not None else '',
                    '坐标': cell.coordinate
                })
        return cells
    
    def _extract_all_styles(self, ws):
        """提取所有单元格样式（完整样式信息）"""
        styles = {}
        for row in ws.iter_rows():
            for cell in row:
                cell_key = cell.coordinate
                style = {}
                
                if cell.font:
                    font_color = self._safe_extract_color(cell.font.color)
                    style['字体'] = {
                        '名称': cell.font.name,
                        '大小': cell.font.size,
                        '粗体': cell.font.bold,
                        '斜体': cell.font.italic,
                        '颜色': font_color,
                        '下划线': cell.font.underline,
                        '删除线': cell.font.strike
                    }
                
                if cell.fill:
                    fg_color = self._safe_extract_color(cell.fill.fgColor)
                    bg_color = self._safe_extract_color(cell.fill.bgColor)
                    if fg_color or bg_color:
                        style['填充'] = {
                            '图案类型': cell.fill.patternType,
                            '前景色': fg_color,
                            '背景色': bg_color
                        }
                
                if cell.border:
                    style['边框'] = {}
                    for side_name in ['left', 'right', 'top', 'bottom']:
                        side_obj = getattr(cell.border, side_name, None)
                        if side_obj and side_obj.style:
                            border_color = self._safe_extract_color(side_obj.color)
                            style['边框'][side_name] = {
                                '样式': side_obj.style,
                                '颜色': border_color
                            }
                
                if cell.alignment:
                    style['对齐'] = {
                        '水平': cell.alignment.horizontal,
                        '垂直': cell.alignment.vertical,
                        '自动换行': cell.alignment.wrapText,
                        '旋转角度': cell.alignment.textRotation
                    }
                
                if cell.number_format and cell.number_format != 'General':
                    style['数字格式'] = cell.number_format
                
                if style:
                    styles[cell_key] = style
        return styles
    
    def _safe_extract_color(self, color_obj):
        if not color_obj:
            return None
        try:
            rgb_val = None
            try:
                rgb_val = color_obj.rgb
            except (TypeError, AttributeError):
                pass

            if rgb_val and isinstance(rgb_val, str) and len(rgb_val) >= 6 and not str(rgb_val).startswith('Values must be'):
                if rgb_val == '00000000':
                    rgb_val = None
                else:
                    if len(rgb_val) == 8:
                        rgb_val = rgb_val[2:]
                    return str(rgb_val)

            if hasattr(color_obj, 'theme') and color_obj.theme is not None:
                theme_colors = {
                    0: 'FFFFFF', 1: '000000', 2: 'EEECE1', 3: '1F497D',
                    4: '4F81BD', 5: 'C0504D', 6: '9BBB59', 7: '8064A2',
                    8: '4BACC6', 9: 'F79646', 10: 'FF0000', 11: 'FFFF00',
                    12: '0000FF', 13: '800080', 14: '008000'
                }
                return theme_colors.get(color_obj.theme)

            if hasattr(color_obj, 'indexed') and color_obj.indexed is not None:
                indexed_colors = {
                    0: '000000', 1: 'FFFFFF', 2: 'FF0000', 3: '00FF00',
                    4: '0000FF', 5: 'FFFF00', 6: 'FF00FF', 7: '00FFFF',
                    8: '000000', 9: 'FFFFFF', 10: 'FF0000', 11: '00FF00',
                    12: '0000FF', 13: 'FFFF00', 14: 'FF00FF', 15: '00FFFF'
                }
                return indexed_colors.get(color_obj.indexed)

            return None
        except Exception:
            return None
    
    def _extract_row_heights(self, ws):
        """提取所有行高"""
        row_heights = {}
        for row_idx in range(1, ws.max_row + 1):
            row_dim = ws.row_dimensions[row_idx]
            if row_dim and row_dim.height:
                row_heights[row_idx] = row_dim.height
        return row_heights
    
    def _extract_page_margins(self, ws):
        """提取页边距"""
        if hasattr(ws, 'page_margins') and ws.page_margins:
            pm = ws.page_margins
            return {
                '左': pm.left,
                '右': pm.right,
                '上': pm.top,
                '下': pm.bottom,
                '页眉': pm.header,
                '页脚': pm.footer
            }
        return {
            '左': 0.71,
            '右': 0.71,
            '上': 0.98,
            '下': 0.98,
            '页眉': 0.5,
            '页脚': 0.5
        }
    
    def _extract_page_setup(self, ws):
        """提取页面设置"""
        paper_size = None
        try:
            paper_size = ws.page_setup.paperSize
        except:
            pass
        
        paper_width = None
        paper_height = None
        try:
            paper_width = ws.page_setup.paperWidth
        except:
            pass
        try:
            paper_height = ws.page_setup.paperHeight
        except:
            pass
        
        orientation = "纵向"
        try:
            if ws.page_setup.orientation == 'landscape':
                orientation = "横向"
        except:
            pass
        
        scale = None
        try:
            scale = ws.page_setup.scale
        except:
            pass
        
        margins = {"上": 72, "右": 54, "下": 72, "左": 54}
        try:
            if ws.page_margins:
                margins["上"] = ws.page_margins.top
                margins["右"] = ws.page_margins.right
                margins["下"] = ws.page_margins.bottom
                margins["左"] = ws.page_margins.left
        except:
            pass
        
        return {
            "纸张类型": paper_size,
            "纸张宽度": paper_width,
            "纸张高度": paper_height,
            "方向": orientation,
            "缩放比例": scale,
            "边距": margins
        }
    
    def _extract_column_widths(self, ws):
        col_widths = []
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            col_dim = ws.column_dimensions.get(col_letter)
            if col_dim and col_dim.width:
                width = col_dim.width
            else:
                width = 8.43
            col_widths.append(width)
        return col_widths
    
    def _extract_rows_data(self, ws):
        """提取行数据"""
        rows_data = []
        
        for row_idx in range(1, ws.max_row + 1):
            row_data = {
                "行号": row_idx,
                "高度": ws.row_dimensions[row_idx].height if ws.row_dimensions[row_idx] and ws.row_dimensions[row_idx].height else 25.0,
                "单元格": []
            }
            
            for col_idx in range(1, ws.max_column + 1):
                cell = ws.cell(row_idx, col_idx)
                
                if cell.coordinate in ws.merged_cells:
                    continue
                
                cell_data = {
                    "列号": col_idx,
                    "文本": str(cell.value) if cell.value is not None else '',
                    "跨行": 1,
                    "跨列": 1,
                    "样式": self._extract_cell_style(cell),
                    "对齐": self._extract_cell_alignment(cell)
                }
                
                for merged_range in ws.merged_cells.ranges:
                    if merged_range.min_row == row_idx and merged_range.min_col == col_idx:
                        cell_data["跨行"] = merged_range.max_row - merged_range.min_row + 1
                        cell_data["跨列"] = merged_range.max_col - merged_range.min_col + 1
                        break
                
                row_data["单元格"].append(cell_data)
            
            rows_data.append(row_data)
        
        return rows_data
    
    def _extract_cell_style(self, cell):
        """提取单元格样式"""
        styles = []
        
        if cell.font:
            if cell.font.size:
                styles.append(f"font-size:{int(cell.font.size)}pt")
            if cell.font.bold:
                styles.append("font-weight:bold")
            if cell.font.name:
                styles.append(f"font-family:{cell.font.name}")
        
        if cell.fill and cell.fill.start_color and cell.fill.start_color.rgb:
            if cell.fill.start_color.rgb != '00000000':
                styles.append(f"background-color:#{cell.fill.start_color.rgb}")
        
        return ";".join(styles) if styles else ""
    
    def _extract_cell_alignment(self, cell):
        """提取单元格对齐方式"""
        if cell.alignment:
            if cell.alignment.horizontal == 'left':
                return 'left'
            elif cell.alignment.horizontal == 'right':
                return 'right'
        return 'center'
    
    def _extract_merged_cells(self, ws):
        """提取合并单元格信息"""
        merged = []
        for merged_range in ws.merged_cells.ranges:
            merged.append({
                "起始": f"{get_column_letter(merged_range.min_col)}{merged_range.min_row}",
                "结束": f"{get_column_letter(merged_range.max_col)}{merged_range.max_row}",
                "起始行": merged_range.min_row,
                "起始列": merged_range.min_col,
                "结束行": merged_range.max_row,
                "结束列": merged_range.max_col
            })
        return merged
    
    def preview_template(self, config):
        """
        预览模板 - 基于完整元数据生成HTML表格，保持与原模板一致
        
        参数:
            config: JSON配置字典
        
        返回:
            HTML字符串
        """
        col_widths = config.get('列宽', [])
        row_heights = config.get('行高', {})
        cells_data = config.get('单元格数据', [])
        styles_data = config.get('样式数据', {})
        merged_cells = config.get('合并单元格', [])
        
        max_row = 0
        max_col = len(col_widths)
        for cell in cells_data:
            max_row = max(max_row, cell['行号'])
        
        merge_map = {}
        for mc in merged_cells:
            for r in range(mc['起始行'], mc['结束行'] + 1):
                for c in range(mc['起始列'], mc['结束列'] + 1):
                    key = f"{r}-{c}"
                    if r == mc['起始行'] and c == mc['起始列']:
                        merge_map[key] = {
                            'rs': mc['结束行'] - mc['起始行'] + 1,
                            'cs': mc['结束列'] - mc['起始列'] + 1,
                            'master': True
                        }
                    else:
                        merge_map[key] = {'master': False}
        
        cell_value_map = {}
        for cell in cells_data:
            cell_value_map[f"{cell['行号']}-{cell['列号']}"] = cell
        
        html = self._build_print_styles(config)
        html += '<table style="border-collapse: collapse; font-family: SimSun, serif;">'
        html += '<colgroup>'
        for w in col_widths:
            pixel_w = int(float(w) * 8)
            html += f'<col style="width: {pixel_w}px;">'
        html += '</colgroup>'
        
        for r in range(1, max_row + 1):
            rh = row_heights.get(str(r), row_heights.get(r, None))
            height_style = f' style="height: {rh}px;"' if rh else ''
            html += f'<tr{height_style}>'
            
            c = 1
            while c <= max_col:
                key = f"{r}-{c}"
                minfo = merge_map.get(key)
                
                if minfo and not minfo['master']:
                    c += 1
                    continue
                
                coord = f"{get_column_letter(c)}{r}"
                style_info = styles_data.get(coord, {})
                
                cell = cell_value_map.get(key, {})
                cv = cell.get('显示值', '')
                if cv is None:
                    cv = ''
                cv = str(cv)
                
                raw_val = cell.get('值', '')
                if raw_val and isinstance(raw_val, str) and '{{' in raw_val:
                    cv = self._resolve_placeholders(raw_val)
                
                cv = cv.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                cv = cv.replace('\n', '<br>')
                
                rowspan = minfo['rs'] if minfo else 1
                colspan = minfo['cs'] if minfo else 1
                
                cell_style = self._build_cell_inline_style(style_info)
                
                rs_attr = f' rowspan="{rowspan}"' if rowspan > 1 else ''
                cs_attr = f' colspan="{colspan}"' if colspan > 1 else ''
                
                html += f'<td style="{cell_style}"{rs_attr}{cs_attr}>{cv or "&nbsp;"}</td>'
                
                c += colspan
            
            html += '</tr>'
        
        html += '</table>'
        return html
    
    def _build_cell_inline_style(self, style_info):
        style_parts = ['padding: 2px 4px']
        
        font_info = style_info.get('字体', {})
        if font_info.get('名称'):
            style_parts.append(f"font-family: '{font_info['名称']}'")
        if font_info.get('大小'):
            style_parts.append(f"font-size: {font_info['大小']}pt")
        if font_info.get('粗体'):
            style_parts.append('font-weight: bold')
        if font_info.get('斜体'):
            style_parts.append('font-style: italic')
        if font_info.get('颜色'):
            style_parts.append(f"color: #{font_info['颜色']}")
        if font_info.get('删除线'):
            style_parts.append('text-decoration: line-through')
        
        fill_info = style_info.get('填充', {})
        if fill_info.get('前景色'):
            style_parts.append(f"background-color: #{fill_info['前景色']}")
        
        border_info = style_info.get('边框', {})
        if border_info:
            border_width_map = {
                'thin': '1px', 'medium': '2px', 'thick': '3px',
                'hair': '0.5px', 'dotted': '1px', 'dashed': '1px',
                'dashDot': '1px', 'dashDotDot': '1px',
                'double': '3px', 'mediumDashed': '2px', 'mediumDashDot': '2px',
                'mediumDashDotDot': '2px', 'slantDashDot': '1px'
            }
            for side in ['top', 'bottom', 'left', 'right']:
                side_info = border_info.get(side)
                if side_info and side_info.get('样式'):
                    color = side_info.get('颜色', '000000')
                    width = border_width_map.get(side_info['样式'], '1px')
                    if color:
                        style_parts.append(f"border-{side}: {width} solid #{color}")
                    else:
                        style_parts.append(f"border-{side}: {width} solid #000")
        else:
            style_parts.append('border: none')
        
        align_info = style_info.get('对齐', {})
        h_align = align_info.get('水平')
        v_align = align_info.get('垂直')
        if h_align:
            style_parts.append(f"text-align: {h_align}")
        if v_align:
            style_parts.append(f"vertical-align: {'middle' if v_align == 'center' else v_align}")
        if align_info.get('自动换行'):
            style_parts.append('white-space: pre-wrap; word-wrap: break-word')
        
        result = '; '.join(style_parts)
        return result
    
    def _resolve_placeholders(self, text, query_params=None):
        import re
        from datetime import datetime as dt
        
        now = dt.now()
        year = now.year
        month = now.month
        
        if query_params and '年月' in query_params:
            ym = query_params['年月']
            parts = ym.split('-')
            if len(parts) == 2:
                year = int(parts[0])
                month = int(parts[1])
        
        def resolve_date(match):
            key = match.group(1).strip()
            
            if key == '年月+1':
                m = month + 1
                y = year
                if m > 12:
                    m = 1
                    y += 1
                return f'{y}年{m}月'
            elif key == '年月-1':
                m = month - 1
                y = year
                if m < 1:
                    m = 12
                    y -= 1
                return f'{y}年{m}月'
            elif key == '年月':
                return f'{year}年{month}月'
            elif key == '年月日':
                return f'{now.year}年{now.month}月{now.day}日'
            elif key == '年':
                return str(year)
            elif key == '月':
                return str(month)
            elif key == '日':
                return str(now.day)
            else:
                return match.group(0)
        
        result = re.sub(r'\{\{([^{}]+)\}\}', resolve_date, str(text))
        return result
    
    def _build_print_styles(self, config):
        page_setup = config.get('页面设置', {})
        orientation = page_setup.get('方向', '纵向')
        css_orientation = 'landscape' if orientation == '横向' else 'portrait'
        
        paper_size_map = {
            1: 'letter', 3: 'tabloid', 4: 'ledger',
            5: 'legal', 8: 'A3', 9: 'A4', 11: 'A5',
            12: 'B4', 13: 'B5',
        }
        
        paper_dimensions = {
            1: (216, 279), 3: (279, 432), 4: (432, 279),
            5: (216, 356), 6: (140, 216), 7: (184, 267),
            8: (297, 420), 9: (210, 297), 10: (210, 297),
            11: (148, 210), 12: (250, 353), 13: (176, 250),
        }
        
        paper_type = page_setup.get('纸张类型')
        
        page_size_name = None
        page_width_mm = None
        page_height_mm = None
        
        if paper_type and paper_type in paper_size_map:
            page_size_name = paper_size_map[paper_type]
        elif paper_type and paper_type in paper_dimensions:
            w, h = paper_dimensions[paper_type]
            if orientation == '横向':
                page_width_mm, page_height_mm = h, w
            else:
                page_width_mm, page_height_mm = w, h
        
        if not page_size_name and not page_width_mm:
            paper_width = page_setup.get('纸张宽度')
            paper_height = page_setup.get('纸张高度')
            if paper_width and paper_height:
                if orientation == '横向':
                    page_width_mm = round(float(paper_height) * 0.3528)
                    page_height_mm = round(float(paper_width) * 0.3528)
                else:
                    page_width_mm = round(float(paper_width) * 0.3528)
                    page_height_mm = round(float(paper_height) * 0.3528)
            else:
                page_size_name = 'A4'
        
        margins = page_setup.get('边距', {})
        top_inch = float(margins.get('上', 0.984))
        right_inch = float(margins.get('右', 0.354))
        bottom_inch = float(margins.get('下', 0.984))
        left_inch = float(margins.get('左', 0.354))
        
        top_mm = round(top_inch * 25.4)
        right_mm = round(right_inch * 25.4)
        bottom_mm = round(bottom_inch * 25.4)
        left_mm = round(left_inch * 25.4)
        
        styles = '<style>'
        
        if page_size_name:
            styles += f'@page {{ size: {page_size_name} {css_orientation}; margin: {top_mm}mm {right_mm}mm {bottom_mm}mm {left_mm}mm; }}'
        else:
            styles += f'@page {{ size: {page_width_mm}mm {page_height_mm}mm; margin: {top_mm}mm {right_mm}mm {bottom_mm}mm {left_mm}mm; }}'
        
        styles += '@media print { '
        styles += 'body { margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }'
        styles += '}'
        styles += 'table { -webkit-print-color-adjust: exact; print-color-adjust: exact; }'
        styles += '</style>'
        return styles
    
    def fill_template_data(self, config, query_params):
        """
        自动填报数据（基于单元格数据直接修改值）
        
        参数:
            config: JSON配置字典（包含字段映射）
            query_params: 查询参数（如：{"职工ID": "xxx", "年月": "2026-05"}）
        
        返回:
            填充后的JSON配置
        """
        filled_config = copy.deepcopy(config)
        
        for cell in filled_config.get('单元格数据', []):
            raw_val = cell.get('值', '')
            if raw_val and isinstance(raw_val, str) and '{{' in raw_val:
                resolved = self._resolve_placeholders(raw_val, query_params)
                cell['值'] = resolved
                cell['显示值'] = resolved
        
        if not config.get('字段映射'):
            return filled_config
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            for field_name, mapping in config['字段映射'].items():
                data_source = mapping.get('数据源')
                if not data_source:
                    continue
                
                table, column = data_source.split('.')
                
                value = self._query_field_value(cursor, table, column, query_params)
                
                if value is not None:
                    target_row = mapping['行']
                    target_col = mapping['列']
                    
                    for cell in filled_config.get('单元格数据', []):
                        if cell['行号'] == target_row and cell['列号'] == target_col:
                            cell['值'] = value
                            cell['显示值'] = str(value)
                            break
                    
                    if '行数据' in filled_config:
                        for row_data in filled_config['行数据']:
                            if row_data['行号'] == target_row:
                                for cell in row_data['单元格']:
                                    if cell['列号'] == target_col:
                                        cell['文本'] = str(value)
                                        break
        finally:
            cursor.close()
            conn.close()
        
        return filled_config
    
    def _query_field_value(self, cursor, table, column, query_params):
        """从数据库查询单个字段值"""
        try:
            if '职工ID' in query_params:
                sql = f"SELECT {column} FROM {table} WHERE id_card = %s LIMIT 1"
                cursor.execute(sql, (query_params['职工ID'],))
            elif '身份证号' in query_params:
                sql = f"SELECT {column} FROM {table} WHERE id_card = %s LIMIT 1"
                cursor.execute(sql, (query_params['身份证号'],))
            else:
                return None
            
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"查询字段值失败: {e}")
            return None
    
    def fill_and_export_from_original(self, original_file_path, mappings, query_params, output_path):
        """
        基于原始Excel文件填充数据并导出（保证100%格式一致）
        
        参数:
            original_file_path: 原始Excel文件路径
            mappings: 字段映射字典
            query_params: 查询参数
            output_path: 输出文件路径
        
        返回:
            输出文件路径
        """
        wb = load_workbook(original_file_path)
        ws = wb.active
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            for field_name, mapping in mappings.items():
                data_source = mapping.get('数据源')
                if not data_source:
                    continue
                
                row_idx = mapping['行']
                col_idx = mapping['列']
                
                table, column = data_source.split('.')
                
                value = self._query_field_value(cursor, table, column, query_params)
                
                if value is not None:
                    ws.cell(row=row_idx, column=col_idx, value=str(value))
        finally:
            cursor.close()
            conn.close()
        
        wb.save(output_path)
        wb.close()
        
        return output_path
    
    def export_to_excel(self, config, output_path):
        """
        导出为Excel文件（基于完整元数据实现100%格式复制）
        
        参数:
            config: JSON配置字典（包含完整元数据）
            output_path: 输出文件路径
        """
        wb = Workbook()
        ws = wb.active
        
        if '页面设置' in config:
            page_setup = config['页面设置']
            ws.page_setup.orientation = 'portrait' if page_setup.get('方向') == '纵向' else 'landscape'
            if page_setup.get('缩放比例'):
                ws.page_setup.scale = page_setup['缩放比例']
            if hasattr(page_setup, 'paperSize'):
                ws.page_setup.paperSize = page_setup['paperSize']
        
        if '页边距' in config:
            margins = config['页边距']
            ws.page_margins.left = margins.get('左', 0.71)
            ws.page_margins.right = margins.get('右', 0.71)
            ws.page_margins.top = margins.get('上', 0.98)
            ws.page_margins.bottom = margins.get('下', 0.98)
            ws.page_margins.header = margins.get('页眉', 0.5)
            ws.page_margins.footer = margins.get('页脚', 0.5)
        
        if '列宽' in config:
            for col_idx, width_val in enumerate(config['列宽'], 1):
                ws.column_dimensions[get_column_letter(col_idx)].width = float(width_val)
        
        if '行高' in config:
            for row_idx, height in config['行高'].items():
                ws.row_dimensions[int(row_idx)].height = height
        
        if '单元格数据' in config and '样式数据' in config:
            for cell_data in config['单元格数据']:
                row_idx = cell_data['行号']
                col_idx = cell_data['列号']
                ws_cell = ws.cell(row_idx, col_idx)
                ws_cell.value = cell_data['值']
                
                cell_key = cell_data['坐标']
                if cell_key in config['样式数据']:
                    self._apply_full_style(ws_cell, config['样式数据'][cell_key])
        
        elif '行数据' in config:
            for row_data in config['行数据']:
                row_idx = row_data['行号']
                if '高度' in row_data:
                    ws.row_dimensions[row_idx].height = row_data['高度']
                
                for cell_data in row_data['单元格']:
                    col_idx = cell_data['列号']
                    ws_cell = ws.cell(row_idx, col_idx)
                    ws_cell.value = cell_data.get('文本', '')
                    
                    if '样式' in cell_data or '对齐' in cell_data:
                        self._apply_cell_style(ws_cell, cell_data)
        
        if '合并单元格' in config:
            for merged in config['合并单元格']:
                if '起始' in merged and '结束' in merged:
                    ws.merge_cells(f"{merged['起始']}:{merged['结束']}")
                elif '起始行' in merged and '起始列' in merged and '结束行' in merged and '结束列' in merged:
                    ws.merge_cells(
                        start_row=merged['起始行'],
                        start_column=merged['起始列'],
                        end_row=merged['结束行'],
                        end_column=merged['结束列']
                    )
        
        wb.save(output_path)
        wb.close()
        
        return output_path
    
    def _apply_cell_style(self, ws_cell, cell_data):
        """应用单元格样式到Excel单元格（简化版）"""
        style = cell_data.get('样式', '')
        
        if 'font-size:' in style:
            import re
            match = re.search(r'font-size:(\d+)pt', style)
            if match:
                ws_cell.font = Font(size=int(match.group(1)))
        
        if 'font-weight:bold' in style:
            ws_cell.font = Font(bold=True)
        
        align = cell_data.get('对齐', 'center')
        if align == 'left':
            ws_cell.alignment = Alignment(horizontal='left', vertical='center')
        elif align == 'right':
            ws_cell.alignment = Alignment(horizontal='right', vertical='center')
        else:
            ws_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    def _apply_full_style(self, ws_cell, style_data):
        """应用完整样式到Excel单元格（实现100%格式复制）"""
        font_props = {}
        if '字体' in style_data:
            font_info = style_data['字体']
            if font_info.get('大小'):
                font_props['size'] = font_info['大小']
            if font_info.get('粗体'):
                font_props['bold'] = font_info['粗体']
            if font_info.get('斜体'):
                font_props['italic'] = font_info['斜体']
            if font_info.get('名称'):
                font_props['name'] = font_info['名称']
            if font_info.get('颜色'):
                from openpyxl.styles.colors import RGB
                font_props['color'] = RGB(font_info['颜色'])
            if font_info.get('下划线'):
                font_props['underline'] = font_info['下划线']
            if font_info.get('删除线'):
                font_props['strike'] = font_info['删除线']
        
        if font_props:
            ws_cell.font = Font(**font_props)
        
        if '填充' in style_data:
            fill_info = style_data['填充']
            if fill_info.get('前景色'):
                from openpyxl.styles.colors import RGB
                fill = PatternFill(
                    patternType=fill_info.get('图案类型', 'solid'),
                    fgColor=RGB(fill_info['前景色'])
                )
                ws_cell.fill = fill
        
        if '边框' in style_data:
            border_info = style_data['边框']
            sides = {}
            for side_name in ['left', 'right', 'top', 'bottom']:
                if side_name in border_info:
                    side_data = border_info[side_name]
                    side_color = None
                    if side_data.get('颜色'):
                        from openpyxl.styles.colors import RGB
                        side_color = RGB(side_data['颜色'])
                    sides[side_name] = Side(
                        style=side_data['样式'],
                        color=side_color
                    )
            if sides:
                ws_cell.border = Border(**sides)
        
        if '对齐' in style_data:
            align_info = style_data['对齐']
            ws_cell.alignment = Alignment(
                horizontal=align_info.get('水平', 'center'),
                vertical=align_info.get('垂直', 'center'),
                wrapText=align_info.get('自动换行', False),
                textRotation=align_info.get('旋转角度', 0)
            )
        
        if '数字格式' in style_data:
            ws_cell.number_format = style_data['数字格式']
    
    def save_template_config(self, config):
        """
        保存模板配置到数据库
        
        参数:
            config: JSON配置字典
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO template_configs (模板ID, 模板名称, 模板类型, 配置JSON, 原始文件路径, 创建时间, 更新时间)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (模板ID) DO UPDATE SET
                    模板名称 = EXCLUDED.模板名称,
                    模板类型 = EXCLUDED.模板类型,
                    配置JSON = EXCLUDED.配置JSON,
                    原始文件路径 = EXCLUDED.原始文件路径,
                    更新时间 = EXCLUDED.更新时间
            """, (
                config['模板ID'],
                config['模板名称'],
                config['模板类型'],
                json.dumps(config, ensure_ascii=False),
                config.get('原始文件', ''),
                config['导入时间'],
                config['导入时间']
            ))
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def load_template_config(self, template_id):
        """
        从数据库加载模板配置
        
        参数:
            template_id: 模板ID
        
        返回:
            JSON配置字典
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 配置JSON FROM template_configs WHERE 模板ID = %s
            """, (template_id,))
            
            row = cursor.fetchone()
            if row:
                config_str = row[0]
                if isinstance(config_str, str):
                    return json.loads(config_str)
                return config_str
            return None
        finally:
            cursor.close()
            conn.close()
    
    def list_templates(self):
        """
        列出所有模板
        
        返回:
            模板列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 模板ID, 模板名称, 模板类型, 原始文件路径, 创建时间, 更新时间
                FROM template_configs
                ORDER BY 创建时间 DESC
            """)
            
            templates = []
            for row in cursor.fetchall():
                templates.append({
                    "模板ID": row[0],
                    "模板名称": row[1],
                    "模板类型": row[2],
                    "原始文件": row[3],
                    "创建时间": row[4],
                    "更新时间": row[5]
                })
            
            return templates
        finally:
            cursor.close()
            conn.close()
    
    def save_field_mapping(self, template_id, field_name, row, col, data_source, transform_func=None, default_value=None):
        """
        保存字段映射
        
        参数:
            template_id: 模板ID
            field_name: 字段名称
            row: 行号
            col: 列号
            data_source: 数据源（表名.字段名）
            transform_func: 转换函数
            default_value: 默认值
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            table, column = data_source.split('.') if '.' in data_source else (data_source, '')
            
            cursor.execute("""
                INSERT INTO template_field_mappings 
                (模板ID, 字段名称, 行号, 列号, 数据源表, 数据源字段, 转换函数, 默认值)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (模板ID, 字段名称) DO UPDATE SET
                    行号 = EXCLUDED.行号,
                    列号 = EXCLUDED.列号,
                    数据源表 = EXCLUDED.数据源表,
                    数据源字段 = EXCLUDED.数据源字段,
                    转换函数 = EXCLUDED.转换单数,
                    默认值 = EXCLUDED.默认值
            """, (
                template_id, field_name, row, col, table, column, transform_func, default_value
            ))
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def load_field_mappings(self, template_id):
        """
        加载字段映射
        
        参数:
            template_id: 模板ID
        
        返回:
            字段映射字典
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 字段名称, 行号, 列号, 数据源表, 数据源字段, 转换函数, 默认值
                FROM template_field_mappings
                WHERE 模板ID = %s
            """, (template_id,))
            
            mappings = {}
            for row in cursor.fetchall():
                field_name = row[0]
                mappings[field_name] = {
                    "行": row[1],
                    "列": row[2],
                    "数据源": f"{row[3]}.{row[4]}" if row[3] and row[4] else None,
                    "转换函数": row[5],
                    "默认值": row[6]
                }
            
            return mappings
        finally:
            cursor.close()
            conn.close()


    def delete_template(self, template_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT 原始文件路径 FROM template_configs WHERE 模板ID = %s", (template_id,))
            row = cursor.fetchone()
            if not row:
                return {"成功": False, "消息": "模板不存在", "已删除文件": False}

            original_filename = row[0] or ''

            cursor.execute("DELETE FROM template_field_mappings WHERE 模板ID = %s", (template_id,))
            cursor.execute("DELETE FROM template_configs WHERE 模板ID = %s", (template_id,))
            conn.commit()

            file_deleted = False
            if original_filename:
                file_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'uploads', 'templates',
                    original_filename
                )
                if os.path.exists(file_path):
                    os.remove(file_path)
                    file_deleted = True

            return {"成功": True, "消息": "模板删除成功", "已删除文件": file_deleted}

        except Exception as e:
            conn.rollback()
            return {"成功": False, "消息": str(e), "已删除文件": False}
        finally:
            cursor.close()
            conn.close()


template_engine = UniversalTemplateEngine()
