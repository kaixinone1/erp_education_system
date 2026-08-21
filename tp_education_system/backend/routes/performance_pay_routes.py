"""
绩效工资审批表路由 - FastAPI版本（精简版：仅保留历史/统计/上传端点）
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from datetime import datetime
import os
import json

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def get_db_connection():
    import psycopg2
    return psycopg2.connect(**DATABASE_CONFIG)

router = APIRouter(prefix="/api/performance-pay-approval", tags=["绩效工资审批"])

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'performance_pay_approval')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups', 'performance_pay_approval')
SCAN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'performance_pay_scans')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(SCAN_DIR, exist_ok=True)


@router.get("/history")
def get_history():
    """获取历史记录列表"""
    return get_history_list()


@router.get("/list")
def get_list(page: int = 1, size: int = 20, year: str = None):
    """获取绩效工资审批列表（支持分页和年份过滤）"""
    result = get_history_list(year)
    
    # 分页处理
    data = result['data']
    total = len(data)
    
    # 计算分页范围
    start = (page - 1) * size
    end = start + size
    paginated_data = data[start:end]
    
    return {"status": "success", "data": paginated_data, "total": total}


def get_history_list(year: str = None):
    """获取历史记录列表（可过滤年份）"""
    history = []
    
    for filename in os.listdir(DATA_DIR):
        if filename.startswith('performance_pay_') and filename.endswith('.json'):
            # 从文件名解析年份（格式: performance_pay_2026_05.json）
            file_year = None
            try:
                parts = filename.replace('performance_pay_', '').replace('.json', '').split('_')
                if len(parts) >= 1:
                    file_year = parts[0]
            except:
                pass
            
            # 如果指定了年份，过滤不匹配的文件
            if year and file_year != year:
                continue
            
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 从文件名解析年月
            year_month = ''
            try:
                parts = filename.replace('performance_pay_', '').replace('.json', '').split('_')
                if len(parts) == 2:
                    year_month = f"{parts[0]}-{parts[1]}"
            except:
                pass
            
            history.append({
                'id': filename.replace('.json', ''),
                'year_month': year_month,
                'report_unit': data.get('填报单位', '') or data.get('report_unit', ''),
                'total_people': data.get('绩效人数合计', 0) or data.get('total_people', 0),
                'total_amount': data.get('绩效工资合计', 0) or data.get('total_amount', 0),
                'town_subsidy_amount': data.get('乡镇补贴合计', 0) or data.get('town_subsidy_amount', 0),
                'town_subsidy_people': data.get('乡镇补贴人数', 0) or data.get('town_subsidy_people', 0),
                'retired_cadre_count': data.get('退休干部人数', 0) or data.get('retired_cadre_count', 0),
                'retired_worker_count': data.get('退休工人数', 0) or data.get('retired_worker_count', 0),
                'retired_cadre_office_count': data.get('离休干部人数', 0) or data.get('retired_cadre_office_count', 0),
                'legacy_total_people': data.get('遗留问题人数', 0) or data.get('legacy_total_people', 0),
                'legacy_total_amount': data.get('遗留问题金额', 0) or data.get('legacy_total_amount', 0),
                'remarks': data.get('备注', '') or data.get('notes', ''),
                'status': 'generated',
                'has_excel': False,
                'has_pdf': False,
                'has_scanned': False,
                'created_at': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # 按年月倒序排序
    history.sort(key=lambda x: x['year_month'], reverse=True)
    
    return {"status": "success", "data": history, "total": len(history)}


@router.get("/download/{id}")
def download_file(id: str):
    """下载历史文件"""
    filename = f"{id}.xlsx"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if os.path.exists(filepath):
        return FileResponse(filepath, filename=filename)
    
    raise HTTPException(status_code=404, detail="文件不存在")


@router.get("/download-pdf/{id}")
def download_pdf(id: str):
    """下载PDF文件"""
    filename = f"{id}.pdf"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if os.path.exists(filepath):
        return FileResponse(filepath, filename=filename)
    
    raise HTTPException(status_code=404, detail="文件不存在")


@router.post("/upload-scan")
def upload_scan(file: UploadFile = File(...), 年月: str = Form(...)):
    """上传签字盖章扫描件"""
    try:
        # 保存文件
        filename = f"绩效工资审批表_{年月}_签字盖章{os.path.splitext(file.filename)[1]}"
        filepath = os.path.join(SCAN_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(file.file.read())
        
        return {
            "status": "success",
            "message": "上传成功",
            "filename": filename,
            "path": filepath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scans")
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
    
    return {"status": "success", "data": scans}


@router.get("/yearly-summary")
def get_yearly_summary(year: int = datetime.now().year):
    """获取年度汇总数据"""
    try:
        # 查找该年份的所有月度数据
        yearly_data = {}
        months = []
        
        for filename in os.listdir(DATA_DIR):
            if filename.startswith(f'performance_pay_{year}_') and filename.endswith('.json'):
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取月份
                month_str = filename.replace(f'performance_pay_{year}_', '').replace('.json', '')
                month = int(month_str)
                months.append(month)
                
                # 累加数据
                for key, value in data.items():
                    if '人数' in key or '合计' in key or '金额' in key:
                        if isinstance(value, (int, float)):
                            if key not in yearly_data:
                                yearly_data[key] = 0
                            yearly_data[key] += value
        
        months.sort()
        
        # 构建汇总信息
        if months:
            start_month = months[0]
            end_month = months[-1]
            summary_note = f"从{year}年{start_month}月汇总至{year}年{end_month}月"
        else:
            summary_note = f"{year}年暂无数据"
        
        return {
            "status": "success",
            "data": yearly_data,
            "months": months,
            "summary_note": summary_note,
            "year": year
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))