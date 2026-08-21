"""
绩效工资历史记录路由 - 为前端历史页面提供API
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import json

router = APIRouter(prefix="/api/performance-pay", tags=["绩效工资历史"])

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "performance_pay_approval")


def get_history_list(year: str = None):
    """获取历史记录列表（可过滤年份）"""
    history = []
    
    if not os.path.exists(DATA_DIR):
        return {"status": "success", "data": [], "total": 0}
    
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


@router.get("/{id}")
def get_detail(id: str):
    """获取审批表详情"""
    filepath = os.path.join(DATA_DIR, f"{id}.json")
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 从文件名解析年月
    year_month = ''
    try:
        parts = id.replace('performance_pay_', '').split('_')
        if len(parts) == 2:
            year_month = f"{parts[0]}-{parts[1]}"
    except:
        pass
    
    result = {
        'id': id,
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
    }
    
    return {"status": "success", "data": result}


@router.get("/{id}/download/{file_type}")
def download_file(id: str, file_type: str):
    """下载文件"""
    # 这个功能需要实际的文件存储支持
    raise HTTPException(status_code=404, detail="文件未找到")


@router.post("/{id}/upload-scanned")
async def upload_scanned(id: str, file: bytes = None):
    """上传扫描件"""
    # 这个功能需要实际的文件存储支持
    return {"status": "success", "message": "上传成功"}
