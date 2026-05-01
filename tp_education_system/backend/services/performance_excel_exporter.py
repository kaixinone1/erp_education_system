"""
绩效工资审批表Excel导出服务
直接基于原始模板复制，只修改数据，100%保留格式
"""
import os
import shutil
from datetime import datetime
from openpyxl import load_workbook
from typing import Dict, List

class PerformancePayExcelExporter:
    """绩效工资审批表Excel导出器 - 原始模板精确复制版"""

    def __init__(self):
        # 原始模板路径
        self.template_path = r"D:\erp_thirteen\数据库信息\模板\义务教育学校教职工绩效工资审批表.xlsx"
        # 导出目录
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'exports'
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def export_with_template(self, data: Dict, year_month: str) -> str:
        """
        基于原始模板导出Excel
        直接复制模板，修改数据，100%保留原始格式
        """
        # 1. 复制原始模板文件
        filename = f"绩效工资审批表_{year_month}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        shutil.copy2(self.template_path, filepath)

        # 2. 打开复制后的文件
        wb = load_workbook(filepath)
        ws = wb.active

        # 3. 修改数据
        self._update_data(ws, data)

        # 4. 保存
        wb.save(filepath)
        return filepath

    def _update_data(self, ws, data: Dict):
        """更新数据到工作表"""
        today = datetime.now()
        today_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

        # ===== 第1行：标题 =====
        ws['B1'] = today_str  # 日期
        ws['D1'] = f"{data.get('年月', '2026年5月')} 义务教育学校教职工绩效工资审批表"

        # ===== 第2行：填报信息 =====
        ws['B2'] = data.get('填报单位', '太平镇中心学校')
        ws['G2'] = today_str

        # ===== 行政管理人员数据（第6-10行）=====
        admin_data = data.get('administrative', {})
        admin_items = ['副处级', '正科级', '副科级', '科员级', '办事员级']
        for i, item in enumerate(admin_items):
            row = 6 + i
            item_data = admin_data.get(item, {})
            ws[f'B{row}'] = item_data.get('count', '')
            ws[f'C{row}'] = item_data.get('standard', '')
            ws[f'D{row}'] = item_data.get('subtotal', '')

        # ===== 专业技术人员数据（第12-16行）=====
        pro_data = data.get('professional', {})
        pro_items = ['正高级', '高级教师', '一级教师', '二级教师', '三级教师']
        for i, item in enumerate(pro_items):
            row = 12 + i
            item_data = pro_data.get(item, {})
            ws[f'B{row}'] = item_data.get('count', '')
            ws[f'C{row}'] = item_data.get('standard', '')
            ws[f'D{row}'] = item_data.get('subtotal', '')

        # ===== 工人数据（第18-23行）=====
        worker_data = data.get('worker', {})
        worker_items = ['高级技师', '技师', '高级工', '中级工', '初级工', '普工']
        for i, item in enumerate(worker_items):
            row = 18 + i
            item_data = worker_data.get(item, {})
            ws[f'B{row}'] = item_data.get('count', '')
            ws[f'C{row}'] = item_data.get('standard', '')
            ws[f'D{row}'] = item_data.get('subtotal', '')

        # ===== 人事部门意见内容（第20-23行）=====
        totals = data.get('totals', {})
        subsidies = data.get('subsidies', {})

        ws['H21'] = totals.get('performance_count', '')
        ws['J21'] = totals.get('performance_total', '')

        ws['H22'] = subsidies.get('count', '')
        ws['J22'] = subsidies.get('total', '')

        total_all = totals.get('performance_total', 0) + subsidies.get('total', 0)
        ws['J23'] = total_all if total_all else ''

        # ===== 绩效工资合计（第24行）=====
        ws['B24'] = totals.get('performance_count', '')
        ws['D24'] = totals.get('performance_total', '')

        # ===== 乡镇补贴合计（第25行）=====
        ws['B25'] = subsidies.get('count', '')
        ws['C25'] = subsidies.get('standard', 350)
        ws['D25'] = subsidies.get('total', '')

        # ===== 岗位设置遗留问题（第26-28行）=====
        legacy = data.get('legacy', [])
        for i in range(3):
            row = 26 + i
            if i < len(legacy):
                item = legacy[i]
                ws[f'B{row}'] = item.get('name', '')
                ws[f'C{row}'] = item.get('amount', '')
                ws[f'D{row}'] = item.get('amount', '')
            else:
                ws[f'B{row}'] = ''
                ws[f'C{row}'] = ''
                ws[f'D{row}'] = ''

        # 合计
        if legacy:
            total_count = sum(1 for item in legacy if item.get('name'))
            total_amount = sum(item.get('amount', 0) for item in legacy)
            ws['B28'] = total_count
            ws['D28'] = total_amount

        # ===== 退休人员（第29-31行）=====
        retirees = data.get('retirees', {})
        ws['B29'] = retirees.get('cadre_count', '')
        ws['B30'] = retirees.get('worker_count', '')
        ws['B31'] = retirees.get('retired_count', '')

        # ===== 备注（第32行）=====
        notes = data.get('notes', '')
        if notes:
            ws['A32'] = f"备注：\n{notes}"


def export_performance_pay(data: Dict, year_month: str) -> str:
    """导出绩效工资审批表的便捷函数"""
    exporter = PerformancePayExcelExporter()
    return exporter.export_with_template(data, year_month)


if __name__ == "__main__":
    # 测试导出
    test_data = {
        '年月': '2026年5月',
        '填报单位': '太平镇中心学校',
        'administrative': {
            '副处级': {'count': 3, 'standard': 3500, 'subtotal': 10500},
            '正科级': {'count': 5, 'standard': 2800, 'subtotal': 14000},
            '副科级': {'count': 8, 'standard': 2200, 'subtotal': 17600},
            '科员级': {'count': 5, 'standard': 1185, 'subtotal': 5925},
            '办事员级': {'count': 2, 'standard': 1106, 'subtotal': 2212},
        },
        'professional': {
            '正高级': {'count': 2, 'standard': 1862, 'subtotal': 3724},
            '高级教师': {'count': 44, 'standard': 1523, 'subtotal': 67012},
            '一级教师': {'count': 136, 'standard': 1309, 'subtotal': 178024},
            '二级教师': {'count': 150, 'standard': 1241, 'subtotal': 186150},
            '三级教师': {'count': 19, 'standard': 1128, 'subtotal': 21432},
        },
        'worker': {
            '高级技师': {'count': 1, 'standard': 1331, 'subtotal': 1331},
            '技师': {'count': 2, 'standard': 1331, 'subtotal': 2662},
            '高级工': {'count': 3, 'standard': 1219, 'subtotal': 3657},
            '中级工': {'count': 5, 'standard': 1185, 'subtotal': 5925},
            '初级工': {'count': 1, 'standard': 1106, 'subtotal': 1106},
            '普工': {'count': 0, 'standard': 1106, 'subtotal': 0},
        },
        'totals': {
            'performance_count': 357,
            'performance_total': 462311,
        },
        'subsidies': {
            'count': 356,
            'standard': 350,
            'total': 124600,
        },
        'legacy': [
            {'name': '李发金', 'amount': 321.3},
            {'name': '张照凯', 'amount': 353.94},
        ],
        'retirees': {
            'cadre_count': 447,
            'worker_count': 2,
            'retired_count': 1,
        },
        'notes': '退休教师死亡2人：赵明安、候兴志'
    }

    path = export_performance_pay(test_data, '2026年5月')
    print(f"Excel导出成功: {path}")