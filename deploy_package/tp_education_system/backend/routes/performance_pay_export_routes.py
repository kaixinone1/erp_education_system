"""
绩效工资审批表导出路由
提供专业的后端Excel导出功能
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any
import os
import json

router = APIRouter(prefix="/api/performance-pay-export", tags=["绩效工资导出"])

# 导入导出服务
from services.performance_excel_exporter import export_performance_pay

class ExportRequest(BaseModel):
    """导出请求模型"""
    data: Dict[str, Any]
    year_month: str

@router.post("/excel")
def export_to_excel(request: ExportRequest):
    """
    导出绩效工资审批表为Excel
    使用openpyxl精确还原模板格式
    """
    try:
        # 调用导出服务
        filepath = export_performance_pay(request.data, request.year_month)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="导出失败")
        
        # 返回文件
        filename = os.path.basename(filepath)
        return FileResponse(
            filepath,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        import traceback
        print(f"导出失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/template-preview")
def preview_template():
    """
    预览模板结构
    返回模板的元数据信息
    """
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data',
        'performance_pay_template.json'
    )
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
        
        return {
            "status": "success",
            "data": {
                "total_rows": template.get('total_rows', 0),
                "total_cols": template.get('total_cols', 0),
                "page_setup": template.get('page_setup', {}),
                "col_widths": template.get('col_widths', []),
                "row_count": len(template.get('rows', []))
            }
        }
    
    raise HTTPException(status_code=404, detail="模板文件不存在")
