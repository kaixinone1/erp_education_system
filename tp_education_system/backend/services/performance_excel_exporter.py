"""
绩效工资审批表Excel导出服务
支持前端发送的扁平数据结构，直接复制原始模板，只修改数据
"""
import os
import shutil
from openpyxl import load_workbook
from typing import Dict, List, Any

class PerformancePayExcelExporter:
    """绩效工资审批表Excel导出器"""

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

        # 3. 设置页面居中（水平居中打印）
        ws.page_setup.centerHorizontally = True
        ws.page_setup.centerVertically = False

        # 4. 转换数据格式（支持扁平结构和嵌套结构）
        normalized_data = self._normalize_data(data)

        # 5. 修改数据
        self._update_data(ws, normalized_data)

        # 6. 保存
        wb.save(filepath)
        return filepath

    def _normalize_data(self, data: Dict) -> Dict:
        """
        将前端发送的扁平结构转换为后端需要的嵌套结构
        前端发送:
        {
            '年月': '2026年5月',
            '填报单位': '太平中心学校',
            '绩效人数合计': 50,
            '绩效工资合计': 65000,
            '在职人数': 45,
            '乡镇补贴标准': 350,
            '乡镇补贴合计': 15750,
            ...
        }

        后端需要:
        {
            '年月': '2026年5月',
            '填报单位': '太平中心学校',
            'totals': {'performance_count': 50, 'performance_total': 65000},
            'subsidies': {'count': 45, 'standard': 350, 'total': 15750},
            'retirees': {'cadre_count': ..., 'worker_count': ..., 'retired_count': ...},
            ...
        }
        """
        normalized = {
            '年月': data.get('年月', data.get('year_month', '')),
            '填报单位': data.get('填报单位', ''),
        }

        # 处理 totals
        normalized['totals'] = {
            'performance_count': data.get('绩效人数合计', data.get('performance_count', 0)),
            'performance_total': data.get('绩效工资合计', data.get('performance_total', 0)),
            'legacy_count': data.get('遗留问题人数', data.get('legacy_count', 0)),
            'legacy_total': data.get('遗留问题金额', data.get('legacy_total', 0)),
        }

        # 处理 subsidies
        normalized['subsidies'] = {
            'count': data.get('在职人数', data.get('subsidies_count', data.get('乡镇补贴人数', 0))),
            'standard': data.get('乡镇补贴标准', data.get('subsidies_standard', 350)),
            'total': data.get('乡镇补贴合计', data.get('subsidies_total', 0)),
        }

        # 处理 retirees
        normalized['retirees'] = {
            'cadre_count': data.get('退休干部', data.get('retirees_cadre_count', 0)),
            'worker_count': data.get('退休职工', data.get('retirees_worker_count', 0)),
            'retired_count': data.get('离休干部人数', data.get('retirees_retired_count', 0)),
        }

        # 处理 notes
        normalized['notes'] = data.get('备注', data.get('notes', ''))

        # 处理无补贴名单
        normalized['no_subsidy_names'] = data.get('无补贴名单', data.get('no_subsidy_names', ''))
        normalized['no_subsidy_count'] = data.get('无补贴人数', data.get('no_subsidy_count', 0))

        # 保留原始的嵌套结构（如果存在）
        if 'administrative' in data:
            normalized['administrative'] = data['administrative']
        if 'professional' in data:
            normalized['professional'] = data['professional']
        if 'worker' in data:
            normalized['worker'] = data['worker']
        if 'legacy' in data:
            normalized['legacy'] = data['legacy']

        return normalized

    def _update_data(self, ws, data: Dict):
        """更新数据到工作表"""
        # ===== 第1行：标题 =====
        # 先取消B1:C1合并，才能修改B1的值
        merged_cells_to_remove = []
        for merge in list(ws.merged_cells.ranges):
            if merge.min_row == 1 and merge.min_col <= 3 and merge.max_col >= 2:
                merged_cells_to_remove.append(merge)

        for merge in merged_cells_to_remove:
            ws.merged_cells.remove(merge)

        ws['B1'] = None  # 清除B1中的原始日期
        ws['D1'] = f"{data.get('年月', '')} 义务教育学校教职工绩效工资审批表"

        # ===== 第2行：填报信息 =====
        ws['B2'] = data.get('填报单位', '')

        # ===== 获取数据 =====
        totals = data.get('totals', {})
        subsidies = data.get('subsidies', {})
        retirees = data.get('retirees', {})
        legacy = data.get('legacy', [])
        no_subsidy_names = data.get('no_subsidy_names', '')
        no_subsidy_count = data.get('no_subsidy_count', 0)

        # ===== 如果有嵌套的详细数据，使用详细数据 ======
        admin_data = data.get('administrative', {})
        pro_data = data.get('professional', {})
        worker_data = data.get('worker', {})

        # ===== 行政管理人员数据（第6-10行）=====
        admin_items = ['副处级', '正科级', '副科级', '科员级', '办事员级']
        for i, item in enumerate(admin_items):
            row = 6 + i
            item_data = admin_data.get(item, {})
            ws[f'B{row}'] = item_data.get('count', '')
            ws[f'C{row}'] = item_data.get('standard', '')
            ws[f'D{row}'] = item_data.get('subtotal', '')

        # ===== 专业技术人员数据（第12-16行）=====
        pro_items = ['正高级', '高级教师', '一级教师', '二级教师', '三级教师']
        for i, item in enumerate(pro_items):
            row = 12 + i
            item_data = pro_data.get(item, {})
            ws[f'B{row}'] = item_data.get('count', '')
            ws[f'C{row}'] = item_data.get('standard', '')
            ws[f'D{row}'] = item_data.get('subtotal', '')

        # ===== 工人数据（第18-23行）=====
        worker_items = ['高级技师', '技师', '高级工', '中级工', '初级工', '普工']
        for i, item in enumerate(worker_items):
            row = 18 + i
            item_data = worker_data.get(item, {})
            ws[f'B{row}'] = item_data.get('count', '')
            ws[f'C{row}'] = item_data.get('standard', '')
            ws[f'D{row}'] = item_data.get('subtotal', '')

        # ===== 人事部门意见内容（第20-23行）=====
        performance_count = totals.get('performance_count', 0)
        performance_total = totals.get('performance_total', 0)
        subsidies_count = subsidies.get('count', 0)
        subsidies_total = subsidies.get('total', 0)

        ws['H21'] = performance_count
        ws['J21'] = performance_total

        ws['H22'] = subsidies_count
        ws['J22'] = subsidies_total

        total_all = performance_total + subsidies_total
        ws['J23'] = total_all if total_all else ''

        # ===== 绩效工资合计（第24行）=====
        ws['B24'] = performance_count
        ws['D24'] = performance_total

        # ===== 乡镇补贴合计（第25行）=====
        ws['B25'] = subsidies_count
        ws['C25'] = subsidies.get('standard', 350)
        ws['D25'] = subsidies_total

        # ===== 岗位设置遗留问题（第26-28行）=====
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


def export_performance_pay_simple(cells: Dict[str, str], year_month: str) -> str:
    """
    简单的导出函数：前端发送每个单元格的内容，后端只写入，不做任何处理
    cells: 字典，键为单元格ID（如"A1", "B2"），值为单元格内容
    """
    # 1. 复制原始模板文件
    template_path = r"D:\erp_thirteen\数据库信息\模板\义务教育学校教职工绩效工资审批表.xlsx"
    output_dir = os.path.join(os.path.dirname(__file__), 'exports')
    os.makedirs(output_dir, exist_ok=True)

    filename = f"绩效工资审批表_{year_month}.xlsx"
    filepath = os.path.join(output_dir, filename)
    shutil.copy2(template_path, filepath)

    # 2. 打开复制后的文件
    wb = load_workbook(filepath)
    ws = wb.active

    # 3. 设置页面居中（水平居中打印）
    ws.page_setup.centerHorizontally = True
    ws.page_setup.centerVertically = False

    # 4. 写入单元格数据（不做任何处理）
    for cell_id, value in cells.items():
        try:
            ws[cell_id] = value if value else None
        except Exception as e:
            print(f"写入单元格 {cell_id} 失败: {e}")

    # 5. 保存
    wb.save(filepath)
    return filepath