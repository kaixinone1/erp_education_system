"""
绩效工资审批表API
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import os
import json
from database.db_pool import get_connection
from utils.excel_export import export_performance_pay_approval
from utils.pdf_export import export_performance_pay_approval_pdf

performance_pay_approval_bp = Blueprint('performance_pay_approval', __name__)

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'performance_pay_approval')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups', 'performance_pay_approval')
SCAN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'performance_pay_scans')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(SCAN_DIR, exist_ok=True)


@performance_pay_approval_bp.route('/current', methods=['GET'])
def get_current_month_data():
    """获取当前月的数据"""
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    filename = f"performance_pay_{year}_{month:02d}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({"status": "success", "data": data})
    
    return jsonify({"status": "success", "data": None})


@performance_pay_approval_bp.route('/save', methods=['POST'])
def save_data():
    """保存数据"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "没有数据"}), 400
    
    # 获取年月
    year_month = data.get('年月', '')
    if year_month:
        try:
            year, month = year_month.replace('年', '-').replace('月', '').split('-')
            year = int(year)
            month = int(month)
        except:
            year = datetime.now().year
            month = datetime.now().month
    else:
        year = datetime.now().year
        month = datetime.now().month
    
    # 保存JSON数据
    filename = f"performance_pay_{year}_{month:02d}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 自动备份Excel
    try:
        excel_path = export_performance_pay_approval(data, BACKUP_DIR)
        print(f"Excel备份已生成: {excel_path}")
    except Exception as e:
        print(f"Excel备份失败: {e}")
    
    # 自动备份PDF
    try:
        pdf_path = export_performance_pay_approval_pdf(data, BACKUP_DIR)
        print(f"PDF备份已生成: {pdf_path}")
    except Exception as e:
        print(f"PDF备份失败: {e}")
    
    return jsonify({"status": "success", "message": "保存成功"})


@performance_pay_approval_bp.route('/load-from-database', methods=['POST'])
def load_from_database():
    """从数据库加载数据"""
    req_data = request.get_json() or {}
    year = req_data.get('year', datetime.now().year)
    month = req_data.get('month', datetime.now().month)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 初始化数据
        data = {
            '填报单位': '太平中心学校',
            '年月': f"{year}年{month}月",
            '填报时间': datetime.now().strftime('%Y年%m月%d日'),
        }
        
        # 1. 从标签关系表获取绩效人员范围
        cursor.execute("""
            SELECT DISTINCT t.教师ID
            FROM 标签关系表 tr
            JOIN 标签字典 td ON tr.标签ID = td.标签ID
            JOIN 教师基础信息 t ON tr.教师ID = t.教师ID
            WHERE td.标签名称 LIKE '%绩效%'
            AND t.任职状态 = '在职'
        """)
        performance_teacher_ids = [row[0] for row in cursor.fetchall()]
        
        # 2. 从岗位聘用信息表获取各岗位人数
        position_counts = {}
        
        # 行政管理人员
        cursor.execute("""
            SELECT 岗位级别, COUNT(*) as 人数
            FROM 岗位聘用信息表
            WHERE 教师ID IN %s
            AND 岗位类别 = '行政管理'
            AND 任职状态 = '现任'
            GROUP BY 岗位级别
        """, (tuple(performance_teacher_ids) if performance_teacher_ids else (None,),))
        
        for row in cursor.fetchall():
            position_counts[row[0]] = row[1]
        
        # 专业技术人员
        cursor.execute("""
            SELECT 岗位级别, COUNT(*) as 人数
            FROM 岗位聘用信息表
            WHERE 教师ID IN %s
            AND 岗位类别 = '专业技术'
            AND 任职状态 = '现任'
            GROUP BY 岗位级别
        """, (tuple(performance_teacher_ids) if performance_teacher_ids else (None,),))
        
        for row in cursor.fetchall():
            position_counts[row[0]] = row[1]
        
        # 工人
        cursor.execute("""
            SELECT 岗位级别, COUNT(*) as 人数
            FROM 岗位聘用信息表
            WHERE 教师ID IN %s
            AND 岗位类别 = '工勤技能'
            AND 任职状态 = '现任'
            GROUP BY 岗位级别
        """, (tuple(performance_teacher_ids) if performance_teacher_ids else (None,),))
        
        for row in cursor.fetchall():
            position_counts[row[0]] = row[1]
        
        # 3. 从绩效工资字典表获取工资标准
        salary_standards = {}
        cursor.execute("""
            SELECT 岗位级别, 月工资标准
            FROM 绩效工资字典表
            WHERE 状态 = '启用'
        """)
        
        for row in cursor.fetchall():
            salary_standards[row[0]] = row[1]
        
        # 填充数据
        # 行政管理人员
        data['副处级人数'] = position_counts.get('副处级', 0)
        data['副处级标准'] = salary_standards.get('副处级', 0)
        data['正科级人数'] = position_counts.get('正科级', 0)
        data['正科级标准'] = salary_standards.get('正科级', 0)
        data['副科级人数'] = position_counts.get('副科级', 0)
        data['副科级标准'] = salary_standards.get('副科级', 0)
        data['科员级人数'] = position_counts.get('科员级', 0)
        data['科员级标准'] = salary_standards.get('科员级', 1185)
        data['办事员级人数'] = position_counts.get('办事员级', 0)
        data['办事员级标准'] = salary_standards.get('办事员级', 0)
        
        # 专业技术人员
        data['正高级教师人数'] = position_counts.get('正高级教师', 0)
        data['正高级教师标准'] = salary_standards.get('正高级教师', 1862)
        data['高级教师人数'] = position_counts.get('高级教师', 0)
        data['高级教师标准'] = salary_standards.get('高级教师', 1523)
        data['一级教师人数'] = position_counts.get('一级教师', 0)
        data['一级教师标准'] = salary_standards.get('一级教师', 1309)
        data['二级教师人数'] = position_counts.get('二级教师', 0)
        data['二级教师标准'] = salary_standards.get('二级教师', 1241)
        data['三级教师人数'] = position_counts.get('三级教师', 0)
        data['三级教师标准'] = salary_standards.get('三级教师', 1128)
        
        # 工人
        data['高级技师人数'] = position_counts.get('高级技师', 0)
        data['高级技师标准'] = salary_standards.get('高级技师', 0)
        data['技师人数'] = position_counts.get('技师', 0)
        data['技师标准'] = salary_standards.get('技师', 1331)
        data['高级工人数'] = position_counts.get('高级工', 0)
        data['高级工标准'] = salary_standards.get('高级工', 1219)
        data['中级工人数'] = position_counts.get('中级工', 0)
        data['中级工标准'] = salary_standards.get('中级工', 1185)
        data['初级工人数'] = position_counts.get('初级工', 0)
        data['初级工标准'] = salary_standards.get('初级工', 1106)
        data['普工人数'] = position_counts.get('普工', 0)
        data['普工标准'] = salary_standards.get('普工', 1106)
        
        # 汇总数据
        total_count = sum([
            data['副处级人数'], data['正科级人数'], data['副科级人数'],
            data['科员级人数'], data['办事员级人数'],
            data['正高级教师人数'], data['高级教师人数'],
            data['一级教师人数'], data['二级教师人数'], data['三级教师人数'],
            data['高级技师人数'], data['技师人数'], data['高级工人数'],
            data['中级工人数'], data['初级工人数'], data['普工人数']
        ])
        data['绩效人数合计'] = total_count
        
        # 计算绩效工资合计
        total_amount = sum([
            data['副处级人数'] * data['副处级标准'],
            data['正科级人数'] * data['正科级标准'],
            data['副科级人数'] * data['副科级标准'],
            data['科员级人数'] * data['科员级标准'],
            data['办事员级人数'] * data['办事员级标准'],
            data['正高级教师人数'] * data['正高级教师标准'],
            data['高级教师人数'] * data['高级教师标准'],
            data['一级教师人数'] * data['一级教师标准'],
            data['二级教师人数'] * data['二级教师标准'],
            data['三级教师人数'] * data['三级教师标准'],
            data['高级技师人数'] * data['高级技师标准'],
            data['技师人数'] * data['技师标准'],
            data['高级工人数'] * data['高级工标准'],
            data['中级工人数'] * data['中级工标准'],
            data['初级工人数'] * data['初级工标准'],
            data['普工人数'] * data['普工标准']
        ])
        data['绩效工资合计'] = total_amount
        
        # 乡镇补贴
        data['在职人数'] = total_count
        data['乡镇补贴标准'] = 350
        data['乡镇补贴合计'] = total_count * 350
        
        # 退休人员统计
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN 个人身份 = '退休干部' THEN 1 ELSE 0 END) as 退休干部,
                SUM(CASE WHEN 个人身份 = '退休工人' THEN 1 ELSE 0 END) as 退休工人,
                SUM(CASE WHEN 个人身份 = '离休干部' THEN 1 ELSE 0 END) as 离休干部
            FROM 教师基础信息
            WHERE 任职状态 IN ('退休', '离休')
        """)
        
        row = cursor.fetchone()
        if row:
            data['退休干部'] = row[0] or 0
            data['退休职工'] = row[1] or 0
            data['离休干部人数'] = row[2] or 0
        
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "data": data})
        
    except Exception as e:
        import traceback
        print(f"加载数据失败: {e}")
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@performance_pay_approval_bp.route('/export', methods=['POST'])
def export_data():
    """导出数据"""
    data = request.get_json()
    format_type = request.args.get('format', 'excel')
    
    if not data:
        return jsonify({"status": "error", "message": "没有数据"}), 400
    
    try:
        if format_type == 'excel':
            filepath = export_performance_pay_approval(data)
            return send_file(filepath, as_attachment=True, download_name=f"绩效工资审批表_{data.get('年月', '未知')}.xlsx")
        elif format_type == 'pdf':
            filepath = export_performance_pay_approval_pdf(data)
            return send_file(filepath, as_attachment=True, download_name=f"绩效工资审批表_{data.get('年月', '未知')}.pdf")
        else:
            return jsonify({"status": "error", "message": "不支持的格式"}), 400
            
    except Exception as e:
        import traceback
        print(f"导出失败: {e}")
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@performance_pay_approval_bp.route('/history', methods=['GET'])
def get_history():
    """获取历史记录列表"""
    history = []
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            history.append({
                'id': filename.replace('.json', ''),
                '年月': data.get('年月', ''),
                '填报单位': data.get('填报单位', ''),
                '绩效人数合计': data.get('绩效人数合计', 0),
                '绩效工资合计': data.get('绩效工资合计', 0),
                '创建时间': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # 按年月倒序排序
    history.sort(key=lambda x: x['年月'], reverse=True)
    
    return jsonify({"status": "success", "data": history})


@performance_pay_approval_bp.route('/download/<id>', methods=['GET'])
def download_file(id):
    """下载历史文件"""
    filename = f"{id}.xlsx"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    
    return jsonify({"status": "error", "message": "文件不存在"}), 404


@performance_pay_approval_bp.route('/upload-scan', methods=['POST'])
def upload_scan():
    """上传签字盖章扫描件"""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "没有文件"}), 400
    
    file = request.files['file']
    year_month = request.form.get('年月', datetime.now().strftime('%Y年%m月'))
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "文件名为空"}), 400
    
    # 保存文件
    filename = f"绩效工资审批表_{year_month}_签字盖章{os.path.splitext(file.filename)[1]}"
    filepath = os.path.join(SCAN_DIR, filename)
    file.save(filepath)
    
    return jsonify({
        "status": "success", 
        "message": "上传成功",
        "filename": filename,
        "path": filepath
    })


@performance_pay_approval_bp.route('/scans', methods=['GET'])
def get_scans():
    """获取扫描件列表"""
    scans = []
    
    for filename in os.listdir(SCAN_DIR):
        filepath = os.path.join(SCAN_DIR, filename)
        scans.append({
            'filename': filename,
            'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
            'size': os.path.getsize(filepath)
        })
    
    scans.sort(key=lambda x: x['upload_time'], reverse=True)
    
    return jsonify({"status": "success", "data": scans})
