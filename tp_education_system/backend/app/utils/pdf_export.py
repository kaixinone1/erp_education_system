"""
PDF导出工具 - 绩效工资审批表
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, pt
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def export_performance_pay_approval_pdf(data, output_dir=None):
    """
    导出绩效工资审批表为PDF
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建文件名
    year_month = data.get('年月', '未知')
    filename = f"绩效工资审批表_{year_month}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # 创建PDF文档
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # 注册中文字体
    try:
        pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
        font_name = 'SimSun'
    except:
        try:
            pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
            font_name = 'SimSun'
        except:
            font_name = 'Helvetica'
    
    # 创建样式
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        alignment=TA_CENTER,
        fontWeight='bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        alignment=TA_LEFT
    )
    
    center_style = ParagraphStyle(
        'CustomCenter',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        alignment=TA_CENTER
    )
    
    right_style = ParagraphStyle(
        'CustomRight',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=16,
        alignment=TA_RIGHT
    )
    
    # 构建表格数据
    table_data = []
    
    # 第1行：标题
    title_row = [
        '',
        Paragraph(year_month, right_style),
        '',
        Paragraph('义务教育学校教职工绩效工资审批表', title_style),
        '', '', '', '', '', '', ''
    ]
    table_data.append(title_row)
    
    # 第2行：填报信息
    info_row = [
        Paragraph('填报单位：', normal_style),
        Paragraph(data.get('填报单位', '太平中心学校'), normal_style),
        '',
        '',
        Paragraph('填报时间:', normal_style),
        Paragraph(data.get('填报时间', ''), normal_style),
        '',
        Paragraph('单位：', normal_style),
        Paragraph('人、元', normal_style),
        '', ''
    ]
    table_data.append(info_row)
    
    # 第3-4行：表头
    header_row1 = [
        Paragraph('项  目', header_style),
        Paragraph('基础性工资', header_style),
        '',
        '',
        Paragraph('呈报单位意见', header_style),
        Paragraph('据实填写，同意呈报。', normal_style),
        '', '', '', '', ''
    ]
    table_data.append(header_row1)
    
    header_row2 = [
        '',
        Paragraph('人数', center_style),
        Paragraph('月工资标准', center_style),
        Paragraph('小计', center_style),
        '', '', '', '', '', '', ''
    ]
    table_data.append(header_row2)
    
    # 行政管理人员
    admin_header = [
        Paragraph('行政管理人员', header_style),
        '', '', '',
        Paragraph('（盖章）', center_style),
        Paragraph(data.get('填报时间', ''), center_style),
        '', '', '', '', ''
    ]
    table_data.append(admin_header)
    
    # 各级别数据
    admin_levels = [
        ('1、副处级', '副处级人数', '副处级标准'),
        ('2、正科级', '正科级人数', '正科级标准'),
        ('3、副科级', '副科级人数', '副科级标准'),
    ]
    
    for label, count_key, std_key in admin_levels:
        count = data.get(count_key, 0)
        std = data.get(std_key, 0)
        subtotal = count * std if count and std else 0
        
        row = [
            Paragraph(label, normal_style),
            Paragraph(str(count) if count else '', center_style),
            Paragraph(str(std) if std else '', center_style),
            Paragraph(str(subtotal) if subtotal else '', center_style),
            '', '', '', '', '', '', ''
        ]
        table_data.append(row)
    
    # 科员级（带教育局意见）
    count = data.get('科员级人数', 0)
    std = data.get('科员级标准', 1185)
    subtotal = count * std if count else 0
    
    row = [
        Paragraph('4、科员级', normal_style),
        Paragraph(str(count) if count else '', center_style),
        Paragraph(str(std), center_style),
        Paragraph(str(subtotal) if subtotal else '', center_style),
        Paragraph('教育局意见', header_style),
        Paragraph('（盖章）', center_style),
        '', '', '', '', ''
    ]
    table_data.append(row)
    
    # 办事员级
    count = data.get('办事员级人数', 0)
    std = data.get('办事员级标准', 0)
    subtotal = count * std if count and std else 0
    
    row = [
        Paragraph('5、办事员级', normal_style),
        Paragraph(str(count) if count else '', center_style),
        Paragraph(str(std) if std else '', center_style),
        Paragraph(str(subtotal) if subtotal else '', center_style),
        '', '', '', '', '', '', ''
    ]
    table_data.append(row)
    
    # 专业技术人员
    teacher_header = [
        Paragraph('专业技术人员', header_style),
        '', '', '', '', '', '', '', '', '', ''
    ]
    table_data.append(teacher_header)
    
    # 教师级别数据
    teacher_levels = [
        ('1、正高级教师', '正高级教师人数', '正高级教师标准', 1862),
        ('2、高级教师', '高级教师人数', '高级教师标准', 1523),
        ('3、一级教师', '一级教师人数', '一级教师标准', 1309),
        ('4、二级教师', '二级教师人数', '二级教师标准', 1241),
        ('5、三级教师', '三级教师人数', '三级教师标准', 1128),
    ]
    
    for i, (label, count_key, std_key, default_std) in enumerate(teacher_levels):
        count = data.get(count_key, 0)
        std = data.get(std_key, default_std)
        subtotal = count * std if count else 0
        
        if i == 0:
            # 第一行添加人事部门意见
            approval_text = f"""根据相关文件及有关规定，经审核，同意你单位：

基础性绩效工资 {data.get('绩效人数合计', 0)}人：{data.get('绩效工资合计', 0)}元；
生活补贴 {data.get('在职人数', 0)}人：{data.get('乡镇补贴合计', 0)}元；
岗位设置遗留问题 {data.get('遗留问题人数', 0)}人：{data.get('遗留问题金额', 0)}元；

合计：{data.get('绩效工资合计', 0) + data.get('乡镇补贴合计', 0) + data.get('遗留问题金额', 0)}元

注：无生活补贴 {data.get('无补贴人数', 0)}人：{data.get('无补贴名单', '')}

{data.get('填报时间', '')}"""
            
            row = [
                Paragraph(label, normal_style),
                Paragraph(str(count) if count else '', center_style),
                Paragraph(str(std), center_style),
                Paragraph(str(subtotal) if subtotal else '', center_style),
                Paragraph('人事部门意见', header_style),
                Paragraph(approval_text, normal_style),
                '', '', '', '', ''
            ]
        else:
            row = [
                Paragraph(label, normal_style),
                Paragraph(str(count) if count else '', center_style),
                Paragraph(str(std), center_style),
                Paragraph(str(subtotal) if subtotal else '', center_style),
                '', '', '', '', '', '', ''
            ]
        table_data.append(row)
    
    # 工人
    worker_header = [
        Paragraph('工人', header_style),
        '', '', '', '', '', '', '', '', '', ''
    ]
    table_data.append(worker_header)
    
    # 工人级别数据
    worker_levels = [
        ('1、高级技师', '高级技师人数', '高级技师标准', 0),
        ('2、技师', '技师人数', '技师标准', 1331),
        ('3、高级工', '高级工人数', '高级工标准', 1219),
        ('4、中级工', '中级工人数', '中级工标准', 1185),
        ('5、初级工', '初级工人数', '初级工标准', 1106),
        ('6、普工', '普工人数', '普工标准', 1106),
    ]
    
    for label, count_key, std_key, default_std in worker_levels:
        count = data.get(count_key, 0)
        std = data.get(std_key, default_std)
        subtotal = count * std if count and std else 0
        
        row = [
            Paragraph(label, normal_style),
            Paragraph(str(count) if count else '', center_style),
            Paragraph(str(std) if std else '', center_style),
            Paragraph(str(subtotal) if subtotal else '', center_style),
            '', '', '', '', '', '', ''
        ]
        table_data.append(row)
    
    # 绩效汇总
    summary_row = [
        Paragraph('绩效人数', header_style),
        Paragraph(str(data.get('绩效人数合计', 0)), center_style),
        Paragraph('绩效合计', header_style),
        Paragraph(str(data.get('绩效工资合计', 0)), center_style),
        '', '', '', '', '', '', ''
    ]
    table_data.append(summary_row)
    
    # 乡镇补贴
    township_row = [
        Paragraph('乡镇工作补贴人数', header_style),
        '',
        Paragraph(str(data.get('在职人数', 0)), center_style),
        Paragraph('标准', header_style),
        Paragraph(str(data.get('乡镇补贴标准', 350)), center_style),
        '',
        Paragraph('金额', header_style),
        Paragraph(str(data.get('乡镇补贴合计', 0)), center_style),
        '', '', ''
    ]
    table_data.append(township_row)
    
    # 退休人员
    retire_row = [
        Paragraph('退休干部人数', header_style),
        Paragraph(str(data.get('退休干部', 0)), center_style),
        Paragraph('退休工人人数', header_style),
        '',
        Paragraph(str(data.get('退休职工', 0)), center_style),
        '',
        Paragraph('离休干部人数', header_style),
        Paragraph(str(data.get('离休干部人数', 0)), center_style),
        '', '', ''
    ]
    table_data.append(retire_row)
    
    # 岗位设置遗留问题
    legacy_row = [
        Paragraph('岗位设置遗留问题', header_style),
        '',
        Paragraph(data.get('遗留问题详情', ''), normal_style),
        '',
        Paragraph('人数', header_style),
        Paragraph(str(data.get('遗留问题人数', 0)), center_style),
        '',
        Paragraph('金额', header_style),
        Paragraph(str(data.get('遗留问题金额', 0)), center_style),
        '', ''
    ]
    table_data.append(legacy_row)
    
    # 备注
    remark_row = [
        Paragraph(f"备注: {data.get('备注', '')}", normal_style),
        '', '', '', '', '', '', '', '', '', ''
    ]
    table_data.append(remark_row)
    
    # 创建表格
    col_widths = [20*mm, 15*mm, 20*mm, 15*mm, 15*mm, 20*mm, 15*mm, 15*mm, 15*mm, 15*mm, 15*mm]
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # 设置表格样式
    table_style = TableStyle([
        # 边框
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        
        # 对齐方式
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # 字体
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        
        # 行高
        ('ROWHEIGHT', (0, 0), (-1, -1), 25),
    ])
    
    table.setStyle(table_style)
    
    # 构建文档
    elements = [table]
    doc.build(elements)
    
    return filepath
