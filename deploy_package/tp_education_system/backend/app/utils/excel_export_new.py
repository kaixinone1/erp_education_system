"""
Excel导出工具 - 绩效工资审批表 (6列版)
严格按照重新设计的6列结构生成
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side


def export_performance_pay_approval_new(data, output_dir=None):
    """
    导出绩效工资审批表为Excel
    6列结构：项目 | 人数 | 标准 | 小计 | 审批意见 | 意见内容
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'exports')
    
    os.makedirs(output_dir, exist_ok=True)
    
    year_month = data.get('年月', '未知')
    filename = f"绩效工资审批表_{year_month}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "绩效工资审批表"
    
    # 页面