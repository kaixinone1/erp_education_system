"""
绩效工资审批表Excel导出服务 - 精确匹配原表格式
完全按照原表的行号、列号、合并单元格结构生成Excel
"""

import os
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins
from typing import Dict, List, Any

class PerformancePayExcelExporter:
    """绩效工资审批表Excel导出器 - 精确还原版"""

    def __init__(self):
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'exports'
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def export_with_template(self, data: Dict, year_month: str) -> str:
        """
        使用模板配置导出Excel - 精确匹配原表
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "绩效工资审批表"

        # 1. 设置页面（A4纵向单面）
        self._setup_page(ws)

        # 2. 设置列宽
        self._setup_columns(ws)

        # 3. 填充所有数据
        self._fill_all_data(ws, data)

        # 4. 合并单元格（严格按照原表结构）
        self._apply_merges(ws)

        # 5. 应用样式
        self._apply_styles(ws)

        # 6. 保存文件
        filename = f"绩效工资审批表_{year_month}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        wb.save(filepath)
        return filepath

    def _setup_page(self, ws):
        """设置页面参数 - A4纵向单面"""
        ws.page_setup.paperSize = 9  # A4
        ws.page_setup.orientation = 'portrait'  # 纵向
        ws.page_setup.fitToPage = False
        ws.page_setup.fitToWidth = False
        ws.page_setup.fitToHeight = False
        ws.page_setup.firstPageNumber = 1
        ws.page_setup.usePageNumbers = True

        # 页边距（英寸）
        ws.page_margins = PageMargins(
            left=0.75, right=0.75, top=1.0, bottom=1.0, header=0.3, footer=0.3
        )

        # 打印区域
        ws.print_area = 'A1:F33'

    def _setup_columns(self, ws):
        """设置列宽 - 原表精确值"""
        # 原表列宽（磅）：84, 100, 100, 100, 75, 75
        widths = [84.0, 100.0, 100.0, 100.0, 75.0, 75.0]
        for i, w in enumerate(widths, 1):
            col_letter = get_column_letter(i)
            ws.column_dimensions[col_letter].width = w / 7.5

    def _fill_all_data(self, ws, data: Dict):
        """填充所有数据 - 严格按照原表行号"""
        today = datetime.now()
        today_str = f"{today.year}年{today.month}月{today.day}日"
        tomorrow = today + timedelta(days=1)
        tomorrow_str = f"{tomorrow.year}年{tomorrow.month}月{tomorrow.day}日"

        # ========== 原表第1行：标题 ==========
        ws['A1'] = f"{data.get('年月', '2026年5月')} 义务教育学校教职工绩效工资审批表"

        # ========== 原表第2行：填报信息 ==========
        ws['A2'] = f"填报单位： {data.get('填报单位', '太平镇中心学校')} 填报时间: {today_str} 单位： 人、元"

        # ========== 原表第3行：表头 ==========
        ws['A3'] = '项目'
        ws['B3'] = '人数'
        ws['C3'] = '标准'
        ws['D3'] = '小计'
        ws['E3'] = '呈报单位意见'
        ws['F3'] = '据实填写，同意呈报。（盖章）2026年4月28日'

        # ========== 原表第4行：行政管理人员分类标题 ==========
        ws['A4'] = '行政管理人员'

        # ========== 原表第5-9行：行政管理人员数据 ==========
        admin_items = ['副处级', '正科级', '副科级', '科员级', '办事员级']
        admin_data = data.get('administrative', {})
        for i, item in enumerate(admin_items):
            row = 5 + i
            ws[f'A{row}'] = f'{i+1}、{item}'
            item_data = admin_data.get(item, {})
            ws[f'B{row}'] = item_data.get('count', '')
            ws[f'C{row}'] = item_data.get('standard', '')
            ws[f'D{row}'] = item_data.get('subtotal', '')

        # ========== 原表第10行：行政管理人员小计 ==========
        # （此行可空，或者放合计数据）

        # ========== 原表第11行：专业技术人员分类标题 ==========
        ws['A11'] = '专业技术人员'

        # ========== 原表第12-16行：专业技术人员数据 ==========
        pro_items = ['正高级', '高级教师', '一级教师', '二级教师', '三级教师']
        pro_data = data.get('professional', {})
        for i, item in enumerate(pro_items):
            row = 12 + i
            ws[f'A{row}'] = f'{i+1}、{item}'
            item_data = pro_data.get(item, {})
            ws[f'B{row}'] = item_data.get('count', '')
            ws[f'C{row}'] = item_data.get('standard', '')
            ws[f'D{row}'] = item_data.get('subtotal', '')

        # ========== 原表第17行：工人分类标题 ==========
        ws['A17'] = '工人'

        # ========== 原表第18-23行：工人数据 ==========
        worker_items = ['高级技师', '技师', '高级工', '中级工', '初级工', '普工']
        worker_data = data.get('worker', {})
        for i, item in enumerate(worker_items):
            row = 18 + i
            ws[f'A{row}'] = f'{i+1}、{item}'
            item_data = worker_data.get(item, {})
            ws[f'B{row}'] = item_data.get('count', '')
            ws[f'C{row}'] = item_data.get('standard', '')
            ws[f'D{row}'] = item_data.get('subtotal', '')

        # ========== 原表第24行：绩效工资合计 ==========
        totals = data.get('totals', {})
        ws['A24'] = '绩效工资合计'
        ws['B24'] = totals.get('performance_count', '')
        ws['D24'] = totals.get('performance_total', '')

        # ========== 原表第25行：乡镇补贴合计 ==========
        subsidies = data.get('subsidies', {})
        ws['A25'] = '乡镇补贴合计'
        ws['B25'] = subsidies.get('count', '')
        ws['C25'] = subsidies.get('standard', '')
        ws['D25'] = subsidies.get('total', '')

        # ========== 原表第26-28行：岗位设置遗留问题 ==========
        legacy = data.get('legacy', [])
        for i in range(3):
            row = 26 + i
            if i < len(legacy):
                item = legacy[i]
                ws[f'A{row}'] = '岗位设置遗留问题'
                ws[f'B{row}'] = item.get('name', '')
                ws[f'C{row}'] = item.get('amount', '')
                ws[f'D{row}'] = item.get('amount', '')
            else:
                ws[f'A{row}'] = '岗位设置遗留问题'

        # ========== 原表第29行：岗位设置遗留问题合计 ==========
        ws['A29'] = '岗位设置遗留问题合计'
        if legacy:
            total_count = sum(1 for item in legacy if item.get('name'))
            total_amount = sum(item.get('amount', 0) for item in legacy)
            ws['B29'] = total_count
            ws['D29'] = total_amount

        # ========== 原表第30行：退休干部 ==========
        retirees = data.get('retirees', {})
        ws['A30'] = '退休干部'
        ws['B30'] = retirees.get('cadre_count', '')

        # ========== 原表第31行：退休工人 ==========
        ws['A31'] = '退休工人'
        ws['B31'] = retirees.get('worker_count', '')

        # ========== 原表第32行：离休干部 ==========
        ws['A32'] = '离休干部'
        ws['B32'] = retirees.get('retired_count', '')

        # ========== 原表第33行：备注 ==========
        ws['A33'] = f"备注：{data.get('notes', '')}"

    def _apply_merges(self, ws):
        """应用合并单元格 - 严格按照原表结构"""
        merges = [
            # 标题行跨6列
            (1, 1, 1, 6),
            # 填报信息行跨6列
            (2, 1, 2, 6),
            # 表头：呈报单位意见跨7行
            (3, 5, 9, 5),
            # 表头：据实填写跨7行
            (3, 6, 9, 6),
            # 行政管理人员分类标题跨4列
            (4, 1, 4, 4),
            # 教育局意见跨9行
            (11, 5, 19, 5),
            # （盖章）跨9行
            (11, 6, 19, 6),
            # 专业技术人员分类标题跨4列
            (11, 1, 11, 4),
            # 人事部门意见跨15行
            (17, 5, 31, 5),
            # 根据相关文件跨15行
            (17, 6, 31, 6),
            # 工人分类标题跨6列
            (17, 1, 17, 4),
            # 备注行跨6列
            (33, 1, 33, 6),
        ]

        for start_row, start_col, end_row, end_col in merges:
            ws.merge_cells(
                start_row=start_row,
                start_column=start_col,
                end_row=end_row,
                end_column=end_col
            )

    def _apply_styles(self, ws):
        """应用单元格样式"""
        thin = Side(style='thin', color='000000')

        # 遍历所有有值的单元格
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None or cell.value == '':
                    continue

                row_num = cell.row
                col_num = cell.column

                # 标题行（第1行）
                if row_num == 1:
                    cell.font = Font(name='宋体', size=16, bold=True)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    continue

                # 填报信息行（第2行）
                if row_num == 2:
                    cell.font = Font(name='宋体', size=11)
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                    continue

                # 表头行（第3行）
                if row_num == 3:
                    cell.font = Font(name='宋体', size=11, bold=True)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                    continue

                # 分类标题行（第4、11、17行）
                if row_num in [4, 11, 17]:
                    cell.font = Font(name='宋体', size=11, bold=True)
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                    continue

                # 合计行（第24、25、29行）
                if row_num in [24, 25, 29]:
                    cell.font = Font(name='宋体', size=11, bold=True)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                    continue

                # 退休人员行（第30、31、32行）
                if row_num in [30, 31, 32]:
                    cell.font = Font(name='宋体', size=11)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                    continue

                # 备注行（第33行）
                if row_num == 33:
                    cell.font = Font(name='宋体', size=11)
                    cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                    continue

                # 垂直文本列（E、F列，从第3行开始）
                if col_num in [5, 6] and row_num >= 3:
                    cell.font = Font(name='宋体', size=11, bold=True)
                    cell.alignment = Alignment(horizontal='center', vertical='center',
                                              text_rotation=255)
                    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                    continue

                # 普通数据单元格（A-D列的数据行）
                if col_num in [1, 2, 3, 4] and row_num >= 5:
                    cell.font = Font(name='宋体', size=11)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                    continue


def export_performance_pay(data: Dict, year_month: str) -> str:
    """导出绩效工资审批表的便捷函数"""
    exporter = PerformancePayExcelExporter()
    return exporter.export_with_template(data, year_month)


if __name__ == "__main__":
    # 测试导出
    test_data = {
        '年月': '2026年5月',
        '填报单位': '太平中心学校',
        '绩效人数合计': 50,
        '绩效工资合计': 65000,
        '在职人数': 45,
        '乡镇补贴标准': 350,
        '乡镇补贴合计': 15750,
        '遗留问题人数': 2,
        '遗留问题金额': 3000,
        '无补贴人数': 5,
        '无补贴名单': '张三、李四、王五',
        'administrative': {
            '副处级': {'count': 3, 'standard': 3500, 'subtotal': 10500},
            '正科级': {'count': 5, 'standard': 2800, 'subtotal': 14000},
            '副科级': {'count': 8, 'standard': 2200, 'subtotal': 17600},
            '科员级': {'count': 12, 'standard': 1800, 'subtotal': 21600},
            '办事员级': {'count': 4, 'standard': 1500, 'subtotal': 6000},
        },
        'professional': {
            '正高级': {'count': 2, 'standard': 3800, 'subtotal': 7600},
            '高级教师': {'count': 10, 'standard': 3200, 'subtotal': 32000},
            '一级教师': {'count': 15, 'standard': 2600, 'subtotal': 39000},
            '二级教师': {'count': 8, 'standard': 2200, 'subtotal': 17600},
            '三级教师': {'count': 3, 'standard': 1800, 'subtotal': 5400},
        },
        'worker': {
            '高级技师': {'count': 1, 'standard': 2800, 'subtotal': 2800},
            '技师': {'count': 2, 'standard': 2400, 'subtotal': 4800},
            '高级工': {'count': 5, 'standard': 2000, 'subtotal': 10000},
            '中级工': {'count': 3, 'standard': 1800, 'subtotal': 5400},
            '初级工': {'count': 2, 'standard': 1600, 'subtotal': 3200},
            '普工': {'count': 1, 'standard': 1400, 'subtotal': 1400},
        },
        'totals': {
            'performance_count': 50,
            'performance_total': 65000,
        },
        'subsidies': {
            'count': 45,
            'standard': 350,
            'total': 15750,
        },
        'legacy': [
            {'name': '张老师', 'amount': 1500},
            {'name': '李老师', 'amount': 1500},
        ],
        'retirees': {
            'cadre_count': 3,
            'worker_count': 5,
            'retired_count': 1,
        },
        'notes': ''
    }

    path = export_performance_pay(test_data, '2026年5月')
    print(f"Excel导出成功: {path}")