import os
import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/template-metadata")
def get_template_metadata():
    """获取绩效审批表模板元数据"""
    template_file = os.path.join(
        os.path.dirname(__file__), 
        '..', 'data', 
        'performance_pay_template.json'
    )
    
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        data = json.loads(content)
        response = JSONResponse(content={"status": "success", "data": data})
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    
    return {"status": "error", "message": "模板元数据不存在"}
