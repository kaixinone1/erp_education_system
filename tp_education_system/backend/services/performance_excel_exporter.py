"""
绩效工资审批表Excel导出服务
支持前端发送的扁平数据结构，直接复制原始模板，只修改数据
"""
import os
import shutil
from datetime import datetime
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
        today = datetime.now()
        today_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

        # ===== 第1行：标题 =====
        ws['B1'] = today_str  # 日期
        ws['D1'] = f"{data.get('年月', '')} 义务教育学校教职工绩效工资审批表"

        # ===== 第2行：填报信息 =====
        ws['B2'] = data.get('填报单位', '')
        ws['G2'] = today_str

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


if __name__ == "__main__":
    # 测试导出 - 使用扁平结构
    test_data = {
        '年月': '2026年5月',
        '填报单位': '太平镇中心学校',
        '绩效人数合计': 357,
        '绩效工资合计': 462311,
        '在职人数': 356,
        '乡镇补贴标准': 350,
        '乡镇补贴合计': 124600,
        '遗留问题人数': 2,
        '遗留问题金额': 675.24,
        '无补贴人数': 1,
        '无补贴名单': '柯坤',
        '退休干部': 447,
        '退休职工': 2,
        '离休干部人数': 1,
        '备注': '退休教师死亡2人：赵明安、候兴志'
    }

    path = export_performance_pay(test_data, '2026年5月')
    print(f"Excel导出成功: {path}")