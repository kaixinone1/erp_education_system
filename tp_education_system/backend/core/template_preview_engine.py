#!/usr/bin/env python3
"""
模板预览引擎 - 将JSON配置转换为Luckysheet格式，实现100%格式还原
核心功能：JSON配置转Luckysheet格式、HTML渲染
"""
from typing import Dict, List, Any

class TemplatePreviewEngine:
    """
    模板预览引擎 - 负责将JSON配置转换为Luckysheet格式和HTML
    """
    
    def __init__(self):
        pass
    
    def convert_to_luckysheet(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        将JSON配置转换为Luckysheet格式
        
        Args:
            config: 模板JSON配置
            
        Returns:
            Luckysheet格式数据
        """
        luckysheet_data = {
            "name": config.get("template_name", "Template"),
            "status": "1",
            "order": "0",
            "celldata": [],
            "config": {
                "row": len(config.get("rows", [])),
                "column": len(config.get("column_widths", [])),
                "defaultColWidth": 80,
                "defaultRowHeight": 24,
                "sheetType": "grid",
                "showGridLines": True,
                "showHeader": False,
                "allowSelect": True,
                "allowEdit": True,
                "allowCopy": True,
                "checkCellFormat": True
            },
            "scrollLeft": 0,
            "scrollTop": 0,
            "selection": [],
            "freeze": {},
            "chart": [],
            "pivotTable": [],
            "filter": {},
            "comment": [],
            "link": [],
            "dataValidation": [],
            "conditionalFormat": [],
            "sort": [],
            "rowHeader": {
                "width": 40
            },
            "columnHeader": {
                "height": 20
            }
        }
        
        # 设置列宽
        col_widths = config.get("column_widths", [])
        colgroup = []
        for idx, width in enumerate(col_widths):
            colgroup.append({
                "id": idx,
                "width": width
            })
        luckysheet_data["config"]["colWidth"] = col_widths
        luckysheet_data["colgroup"] = colgroup
        
        # 设置行高
        rows = config.get("rows", [])
        rowgroup = []
        for idx, row in enumerate(rows):
            height = row.get("height", 24)
            rowgroup.append({
                "id": idx,
                "height": height
            })
        luckysheet_data["config"]["rowHeight"] = [r.get("height", 24) for r in rows]
        luckysheet_data["rowgroup"] = rowgroup
        
        # 填充单元格数据
        celldata = []
        for row_idx, row in enumerate(rows):
            for cell in row.get("cells", []):
                col_idx = cell["column_number"] - 1
                cell_data = {
                    "r": row_idx,
                    "c": col_idx,
                    "v": cell["text"]
                }
                
                # 添加样式
                style = cell.get("style", {})
                style_dict = self._convert_style(style)
                if style_dict:
                    cell_data["m"] = style_dict
                
                celldata.append(cell_data)
        
        luckysheet_data["celldata"] = celldata
        
        # 设置合并单元格
        merged_cells = config.get("merged_cells", [])
        if merged_cells:
            luckysheet_data["merge"] = self._convert_merged_cells(merged_cells)
        
        return luckysheet_data
    
    def _convert_style(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换单元格样式为Luckysheet格式
        """
        result = {}
        
        font = style.get("font", {})
        if font:
            font_style = {}
            if font.get("bold"):
                font_style["bold"] = True
            if font.get("italic"):
                font_style["italic"] = True
            if font.get("underline"):
                font_style["underline"] = True
            if font.get("size"):
                font_style["fontSize"] = font["size"]
            if font.get("name"):
                font_style["fontFamily"] = font["name"]
            if font.get("color"):
                font_style["color"] = font["color"]
            if font_style:
                result["font"] = font_style
        
        fill = style.get("fill", {})
        if fill and fill.get("fg_color"):
            result["bgColor"] = fill["fg_color"]
        
        alignment = style.get("alignment", {})
        if alignment:
            align_style = {}
            if alignment.get("horizontal"):
                align_style["h"] = self._convert_horizontal_alignment(alignment["horizontal"])
            if alignment.get("vertical"):
                align_style["v"] = self._convert_vertical_alignment(alignment["vertical"])
            if alignment.get("wrap_text"):
                align_style["wrap"] = True
            if align_style:
                result["alignment"] = align_style
        
        border = style.get("border", {})
        if border:
            border_style = {}
            border_dict = {}
            
            sides = ["top", "bottom", "left", "right"]
            for side in sides:
                side_data = border.get(side, {})
                if side_data.get("style"):
                    border_dict[side] = {
                        "style": side_data["style"],
                        "color": side_data.get("color") or "#000000"
                    }
            
            if border_dict:
                border_style["borderType"] = "all"
                border_style["borderColor"] = "#000000"
                border_style["borderStyle"] = "thin"
                
                # 详细边框配置
                if border_dict.get("top"):
                    border_style["top"] = border_dict["top"]
                if border_dict.get("bottom"):
                    border_style["bottom"] = border_dict["bottom"]
                if border_dict.get("left"):
                    border_style["left"] = border_dict["left"]
                if border_dict.get("right"):
                    border_style["right"] = border_dict["right"]
                
                result["border"] = border_style
        
        number_format = style.get("number_format")
        if number_format and number_format != "General":
            result["format"] = number_format
        
        return result
    
    def _convert_horizontal_alignment(self, alignment: str) -> str:
        """转换水平对齐方式"""
        mapping = {
            "general": "left",
            "left": "left",
            "center": "center",
            "right": "right",
            "fill": "left",
            "justify": "left",
            "centerContinuous": "center",
            "distributed": "left"
        }
        return mapping.get(alignment, "left")
    
    def _convert_vertical_alignment(self, alignment: str) -> str:
        """转换垂直对齐方式"""
        mapping = {
            "top": "top",
            "center": "middle",
            "bottom": "bottom",
            "justify": "middle",
            "distributed": "middle"
        }
        return mapping.get(alignment, "bottom")
    
    def _convert_merged_cells(self, merged_cells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """转换合并单元格为Luckysheet格式"""
        result = []
        
        for merged in merged_cells:
            result.append({
                "r": merged["start_row"] - 1,
                "c": merged["start_col"] - 1,
                "rs": merged["end_row"] - merged["start_row"] + 1,
                "cs": merged["end_col"] - merged["start_col"] + 1
            })
        
        return result
    
    def convert_to_html(self, config: Dict[str, Any]) -> str:
        """
        将JSON配置转换为HTML表格
        
        Args:
            config: 模板JSON配置
            
        Returns:
            HTML字符串
        """
        rows = config.get("rows", [])
        col_widths = config.get("column_widths", [])
        merged_cells = config.get("merged_cells", [])
        
        # 构建样式字符串
        html = '<!DOCTYPE html>\n<html>\n<head>\n'
        html += '<meta charset="UTF-8">\n'
        html += '<title>模板预览</title>\n'
        html += '<style>\n'
        html += '.preview-table { border-collapse: collapse; table-layout: fixed; }\n'
        html += '.preview-table td { border: 1px solid #ccc; padding: 2px 4px; overflow: hidden; }\n'
        html += '</style>\n'
        html += '</head>\n<body>\n'
        
        # 开始表格
        html += '<table class="preview-table">'
        
        # 列宽定义
        html += '<colgroup>'
        for width in col_widths:
            html += f'<col style="width: {width}px;">'
        html += '</colgroup>'
        
        # 处理合并单元格
        merged_map = {}
        for merged in merged_cells:
            key = f"{merged['start_row']}-{merged['start_col']}"
            merged_map[key] = {
                "rowspan": merged["end_row"] - merged["start_row"] + 1,
                "colspan": merged["end_col"] - merged["start_col"] + 1
            }
        
        # 渲染行
        for row in rows:
            html += f'<tr style="height: {row.get("height", 24)}px;">'
            
            for cell in row.get("cells", []):
                row_num = row["row_number"]
                col_num = cell["column_number"]
                key = f"{row_num}-{col_num}"
                
                # 检查是否是合并单元格的起始位置
                if key in merged_map:
                    merged = merged_map[key]
                    html += self._render_cell(cell, merged["rowspan"], merged["colspan"])
                else:
                    # 检查是否被合并覆盖
                    is_merged = False
                    for m in merged_cells:
                        if (m["start_row"] <= row_num <= m["end_row"] and 
                            m["start_col"] <= col_num <= m["end_col"] and
                            (m["start_row"] != row_num or m["start_col"] != col_num)):
                            is_merged = True
                            break
                    
                    if not is_merged:
                        html += self._render_cell(cell, 1, 1)
            
            html += '</tr>'
        
        html += '</table>\n</body>\n</html>'
        
        return html
    
    def _render_cell(self, cell: Dict[str, Any], rowspan: int, colspan: int) -> str:
        """渲染单个单元格"""
        style = cell.get("style", {})
        style_str = self._build_css_style(style)
        
        attrs = []
        if rowspan > 1:
            attrs.append(f'rowspan="{rowspan}"')
        if colspan > 1:
            attrs.append(f'colspan="{colspan}"')
        
        attrs_str = ' '.join(attrs) if attrs else ''
        
        return f'<td {attrs_str} style="{style_str}">{cell["text"]}</td>'
    
    def _build_css_style(self, style: Dict[str, Any]) -> str:
        """构建CSS样式字符串"""
        styles = []
        
        font = style.get("font", {})
        if font.get("bold"):
            styles.append("font-weight: bold")
        if font.get("italic"):
            styles.append("font-style: italic")
        if font.get("underline"):
            styles.append("text-decoration: underline")
        if font.get("size"):
            styles.append(f"font-size: {font['size']}pt")
        if font.get("name"):
            styles.append(f"font-family: {font['name']}")
        if font.get("color"):
            color = font["color"]
            if color.startswith("FF"):
                color = f"#{color[2:]}"
            styles.append(f"color: {color}")
        
        fill = style.get("fill", {})
        if fill.get("fg_color"):
            color = fill["fg_color"]
            if color.startswith("FF"):
                color = f"#{color[2:]}"
            styles.append(f"background-color: {color}")
        
        alignment = style.get("alignment", {})
        if alignment.get("horizontal"):
            align = self._convert_horizontal_alignment(alignment["horizontal"])
            styles.append(f"text-align: {align}")
        if alignment.get("vertical"):
            align = self._convert_vertical_alignment(alignment["vertical"])
            styles.append(f"vertical-align: {align}")
        if alignment.get("wrap_text"):
            styles.append("white-space: pre-wrap")
        
        return "; ".join(styles)

# 单例导出
template_preview_engine = TemplatePreviewEngine()