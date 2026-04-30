"""
绩效工资审批表专业Excel导出服务
100%还原原始模板格式
使用openpyxl精确控制：
- 单元格大小、字形字号、行高列宽
- 对齐方式、边框样式
- 合并单元格
- A4纸张、页边距设置
- 纵向单面打印
"""

import os
import json
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill, Protection
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins
from typing import Dict, Optional

class PerformancePayExcelExporter:
    """绩效工资审批表Excel导出器"""

    def __init__(self):
        self.template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'performance_pay_template.json'
        )
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'exports'
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def load_template(self) -> Dict:
        """加载模板元数据"""
        if os.path.exists(self.template_path):
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_template()

    def _get_default_template(self) -> Dict:
        """获取默认模板结构"""
        return {
            "page_setup": {
                "margins": {"top": 72, "right": 54, "bottom": 72, "left": 54},
                "paper_width": 595,
                "paper_height": 842,
                "orientation": "portrait"
            },
            "col_widths": ["84", "100", "100", "100", "75", "auto"],
            "rows": []
        }

    def export(self, data: Dict, year_month: str) -> str:
        """
        导出绩效工资审批表为Excel
        :param data: 数据字典
        :param year_month: 年月字符串，如"2026年5月"
        :return: 生成的Excel文件路径
        """
        template = self.load_template()

        # 创建工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = "绩效工资审批表"

        # 设置页面（A4纸张、纵向单面）
        self._setup_page(ws, template)

        # 设置列宽
        self._setup_columns(ws, template)

        # 创建样式
        styles = self._create_styles()

        # 填充数据
        self._fill_data(ws, template, data, styles)

        # 生成文件名
        filename = f"绩效工资审批表_{year_month}.xlsx"
        filepath = os.path.join(self.output_dir, filename)

        # 保存文件
        wb.save(filepath)

        return filepath

    def _setup_page(self, ws, template: Dict):
        """设置页面参数 - A4纵向单面"""
        page_setup = template.get('page_setup', {})

        # A4纸张 (paperSize = 9 表示A4)
        ws.page_setup.paperSize = 9

        # 纵向打印（不是横向）
        ws.page_setup.orientation = 'portrait'

        # 禁止缩放 - 确保100%比例打印
        ws.page_setup.fitToPage = False
        ws.page_setup.fitToWidth = False
        ws.page_setup.fitToHeight = False

        # 确保是单面打印
        ws.page_setup.firstPageNumber = 1
        ws.page_setup.usePageNumbers = True

        # 页边距设置（单位：英寸）
        # 模板中是磅值（1磅 = 1/72英寸），所以除以72转换
        margins = page_setup.get('margins', {})
        ws.page_margins = PageMargins(
            left=margins.get('left', 54) / 72.0,   # 0.75英寸
            right=margins.get('right', 54) / 72.0,  # 0.75英寸
            top=margins.get('top', 72) / 72.0,     # 1英寸
            bottom=margins.get('bottom', 72) / 72.0, # 1英寸
            header=0.3,
            footer=0.3
        )

        # 设置打印区域
        ws.print_area = f'A1:F31'

        # 设置打印选项
        ws.oddHeader.center.text = ""
        ws.oddFooter.center.text = ""
        ws.oddFooter.left.text = ""
        ws.oddFooter.right.text = ""

    def _setup_columns(self, ws, template: Dict):
        """设置列宽 - 精确匹配模板"""
        col_widths = template.get('col_widths', ['84', '100', '100', '100', '75', 'auto'])

        # Excel列宽计算公式：列宽(字符数) = 实际宽度(磅) / 7.5
        # 根据宋体11号字体测试，1个字符约等于7.5磅宽度
        for i, width in enumerate(col_widths, 1):
            col_letter = get_column_letter(i)
            if width == 'auto':
                ws.column_dimensions[col_letter].width = 18
            else:
                # 直接使用模板中的宽度值，转换为Excel列宽单位
                # 模板宽度单位是磅，Excel列宽单位是字符数
                # 84磅 ≈ 11.2个字符宽度
                ws.column_dimensions[col_letter].width = round(float(width) / 7.5, 2)

    def _create_styles(self):
        """创建样式字典"""
        # 细边框 - 0.5pt
        thin_border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )

        # 中等边框 - 1pt
        medium_border = Border(
            left=Side(style='medium', color='000000'),
            right=Side(style='medium', color='000000'),
            top=Side(style='medium', color='000000'),
            bottom=Side(style='medium', color='000000')
        )

        # 右边框 - 1pt (用于某些单元格的右侧分隔)
        right_border = Border(
            right=Side(style='medium', color='000000')
        )

        # 下边框 - 0.5pt (用于表头等)
        bottom_border = Border(
            bottom=Side(style='thin', color='000000')
        )

        return {
            'title': {
                'font': Font(name='宋体', size=16, bold=True),
                'alignment': Alignment(horizontal='center', vertical='center'),
                'border': None
            },
            'info': {
                'font': Font(name='宋体', size=11),
                'alignment': Alignment(horizontal='left', vertical='center'),
                'border': None
            },
            'header': {
                'font': Font(name='宋体', size=11, bold=True),
                'alignment': Alignment(horizontal='center', vertical='center'),
                'border': thin_border
            },
            'normal': {
                'font': Font(name='宋体', size=11),
                'alignment': Alignment(horizontal='center', vertical='center'),
                'border': thin_border
            },
            'normal_left': {
                'font': Font(name='宋体', size=11),
                'alignment': Alignment(horizontal='left', vertical='center'),
                'border': thin_border
            },
            'vertical_text': {
                'font': Font(name='宋体', size=11, bold=True),
                'alignment': Alignment(horizontal='center', vertical='center', text_rotation=255),
                'border': thin_border
            },
            'remarks': {
                'font': Font(name='宋体', size=11),
                'alignment': Alignment(horizontal='left', vertical='top', wrap_text=True),
                'border': thin_border
            },
            'thin_border': thin_border,
            'medium_border': medium_border,
            'right_border': right_border,
            'bottom_border': bottom_border
        }

    def _fill_data(self, ws, template: Dict, data: Dict, styles: Dict):
        """填充数据到工作表"""
        rows = template.get('rows', [])
        occupied_cells = {}

        for row_idx, row in enumerate(rows, 1):
            row_height = row.get('height', 25)
            ws.row_dimensions[row_idx].height = row_height

            col_idx = 1
            for cell in row.get('cells', []):
                # 检查是否被合并单元格占用
                while occupied_cells.get(f"{row_idx}-{col_idx}"):
                    col_idx += 1
                    if col_idx > 6:
                        break

                if col_idx > 6:
                    break

                text = cell.get('text', '')
                rowspan = cell.get('rowspan', 1)
                colspan = cell.get('colspan', 1)
                cell_class = cell.get('class', '')
                align = cell.get('align', 'center')
                is_notes_row = cell.get('isNotesRow', False)
                no_border = cell.get('no_border', False)
                style_info = cell.get('style', '')

                # 替换日期占位符
                text = self._replace_placeholders(text, data)

                # 合并单元格
                if rowspan > 1 or colspan > 1:
                    ws.merge_cells(
                        start_row=row_idx,
                        start_column=col_idx,
                        end_row=row_idx + rowspan - 1,
                        end_column=col_idx + colspan - 1
                    )

                    # 标记被占用的单元格
                    for r in range(row_idx, row_idx + rowspan):
                        for c in range(col_idx, col_idx + colspan):
                            occupied_cells[f"{r}-{c}"] = True

                # 设置单元格值
                cell_obj = ws.cell(row=row_idx, column=col_idx, value=text)

                # 设置样式
                self._apply_cell_style(cell_obj, cell_class, align, is_notes_row, no_border, style_info, styles)

    def _replace_placeholders(self, text: str, data: Dict) -> str:
        """替换文本中的占位符"""
        if not text:
            return text

        # 替换日期
        today = datetime.now()
        today_str = f"{today.year}年{today.month}月{today.day}日"

        # 正确计算明天（避免月末问题）
        tomorrow = today + timedelta(days=1)
        tomorrow_str = f"{tomorrow.year}年{tomorrow.month}月{tomorrow.day}日"

        text = text.replace('2026年5月', data.get('年月', ''))
        text = text.replace('2026年4月28日', today_str)
        text = text.replace('2026年4月29日', tomorrow_str)

        # 替换数据占位符
        text = text.replace('0人，0元', f"{data.get('绩效人数合计', 0)}人，{data.get('绩效工资合计', 0)}元")
        text = text.replace('生活补贴0人，0元', f"生活补贴{data.get('在职人数', 0)}人，{data.get('乡镇补贴合计', 0)}元")
        text = text.replace('岗位设置遗留0人，0元', f"岗位设置遗留{data.get('遗留问题人数', 0)}人，{data.get('遗留问题金额', 0)}元")
        text = text.replace('无乡镇补贴0人，姓名', f"无乡镇补贴{data.get('无补贴人数', 0)}人，{data.get('无补贴名单', '')}")

        total = data.get('绩效工资合计', 0) + data.get('乡镇补贴合计', 0) + data.get('遗留问题金额', 0)
        text = text.replace('总计0人，0元', f"总计{total}元")
        text = text.replace('合计0人，0元', f"合计{data.get('绩效工资合计', 0) + data.get('乡镇补贴合计', 0)}元")

        return text

    def _apply_cell_style(self, cell, cell_class: str, align: str, is_notes_row: bool, no_border: bool, style_info: str, styles: Dict):
        """应用单元格样式"""
        # 如果是无边框单元格
        if no_border:
            cell.border = None
            cell.font = Font(name='宋体', size=11)
            if align == 'center':
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif align == 'left':
                cell.alignment = Alignment(horizontal='left', vertical='center')
            else:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            return

        # 根据单元格类型选择样式
        if cell_class in ['title', 'xl75']:
            style = styles['title']
        elif cell_class in ['info']:
            style = styles['info']
        elif cell_class in ['xl78', 'xl107', 'xl122']:
            # 垂直文本 - 用于"呈报单位意见"、"教育局意见"、"人事部门意见"
            style = styles['vertical_text']
        elif cell_class in ['xl80', 'xl90', 'xl104']:
            # 分类标题（行政管理人员、专业技术人员、工人）
            style = styles['header']
            style['alignment'] = Alignment(horizontal='left', vertical='center')
        elif is_notes_row or cell_class == 'xl131':
            style = styles['remarks']
        else:
            style = styles['normal']

        # 设置字体
        cell.font = style['font']

        # 设置对齐方式
        if align == 'left':
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        elif align == 'right':
            cell.alignment = Alignment(horizontal='right', vertical='center')
        else:
            cell.alignment = style['alignment']

        # 设置边框
        if style.get('border'):
            cell.border = style['border']

        # 处理style中的特殊边框设置
        if 'border-right:1.0pt solid' in style_info:
            # 右边框为1pt
            current_border = cell.border
            cell.border = Border(
                left=current_border.left if current_border.left else Side(style='thin', color='000000'),
                right=Side(style='medium', color='000000'),
                top=current_border.top if current_border.top else Side(style='thin', color='000000'),
                bottom=current_border.bottom if current_border.bottom else Side(style='thin', color='000000')
            )
        if 'border-bottom:.5pt solid' in style_info:
            # 下边框为0.5pt
            current_border = cell.border
            cell.border = Border(
                left=current_border.left if current_border.left else Side(style='thin', color='000000'),
                right=current_border.right if current_border.right else Side(style='thin', color='000000'),
                top=current_border.top if current_border.top else Side(style='thin', color='000000'),
                bottom=Side(style='thin', color='000000')
            )

def export_performance_pay(data: Dict, year_month: str) -> str:
    """
    导出绩效工资审批表的便捷函数
    :param data: 数据字典
    :param year_month: 年月字符串
    :return: Excel文件路径
    """
    exporter = PerformancePayExcelExporter()
    return exporter.export(data, year_month)

if __name__ == "__main__":
    # 测试导出
    test_data = {
        '年月': '2026年5月',
        '填报单位': '太平中心学校',
        '填报时间': '2026年4月28日',
        '绩效人数合计': 50,
        '绩效工资合计': 65000,
        '在职人数': 45,
        '乡镇补贴标准': 350,
        '乡镇补贴合计': 15750,
        '遗留问题人数': 2,
        '遗留问题金额': 3000,
        '无补贴人数': 5,
        '无补贴名单': '张三、李四、王五'
    }

    path = export_performance_pay(test_data, '2026年5月')
    print(f"Excel导出成功: {path}")