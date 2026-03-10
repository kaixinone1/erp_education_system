"""
清单模板管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import psycopg2
from datetime import datetime
import json

router = APIRouter(prefix="/api/checklist-template", tags=["清单模板"])

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


@router.get("/target-options")
async def get_target_options():
    """获取目标选项列表"""
    from utils.target_mapping import get_all_target_options
    return {"status": "success", "data": get_all_target_options()}


@router.get("/employment-status-options")
async def get_employment_status_options():
    """获取任职状态选项列表 - 从字典表读取"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 从字典表查询任职状态选项
        cursor.execute("""
            SELECT employment_status, status_code, sort_order_sequence
            FROM dict_dictionary
            WHERE shi_fou_you_xiao = '是'
            ORDER BY sort_order_sequence::int
        """)

        rows = cursor.fetchall()
        options = []
        for row in rows:
            status = row[0]
            if status:  # 确保不为空
                options.append({"value": status, "label": status})

        cursor.close()
        conn.close()

        return {"status": "success", "data": options}
    except Exception as e:
        print(f"获取任职状态选项失败: {e}")
        # 如果查询失败，返回默认值
        return {"status": "success", "data": [
            {"value": "在职", "label": "在职"},
            {"value": "退休", "label": "退休"},
            {"value": "离休", "label": "离休"},
            {"value": "调离", "label": "调离"},
            {"value": "调出", "label": "调出"},
            {"value": "离职", "label": "离职"},
            {"value": "去世", "label": "去世"}
        ]}


@router.get("/list")
async def get_checklist_templates():
    """获取清单模板列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, 清单名称, 触发条件, 任务项列表, 是否有效, created_at, updated_at
            FROM business_checklist
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        result = []

        for row in rows:
            result.append({
                "id": row[0],
                "清单名称": row[1],
                "触发条件": row[2],
                "任务项列表": row[3],
                "是否有效": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[6].isoformat() if row[6] else None
            })

        cursor.close()
        conn.close()

        return {"status": "success", "data": result}
    except Exception as e:
        print(f"获取清单模板列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}")
async def get_checklist_template(template_id: int):
    """获取单个清单模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, 清单名称, 触发条件, 任务项列表, 是否有效, created_at, updated_at, 关联模板ID
            FROM business_checklist
            WHERE id = %s
        """, (template_id,))

        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="清单模板不存在")

        result = {
            "id": row[0],
            "清单名称": row[1],
            "触发条件": row[2],
            "任务项列表": row[3],
            "是否有效": row[4],
            "created_at": row[5].isoformat() if row[5] else None,
            "updated_at": row[6].isoformat() if row[6] else None,
            "关联模板ID": row[7]
        }

        cursor.close()
        conn.close()

        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取清单模板失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_checklist_template(data: dict):
    """创建清单模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        清单名称 = data.get("清单名称")
        触发条件 = data.get("触发条件")
        任务项列表 = data.get("任务项列表")
        是否有效 = data.get("是否有效", True)
        关联模板ID = data.get("关联模板ID")

        cursor.execute("""
            INSERT INTO business_checklist (清单名称, 触发条件, 任务项列表, 是否有效, 关联模板ID, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (清单名称, json.dumps(触发条件) if 触发条件 else None,
              json.dumps(任务项列表) if 任务项列表 else None,
              是否有效, 关联模板ID, datetime.now(), datetime.now()))

        new_id = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "id": new_id, "message": "清单模板创建成功"}
    except Exception as e:
        conn.rollback()
        print(f"创建清单模板失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}")
async def update_checklist_template(template_id: int, data: dict):
    """更新清单模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否存在
        cursor.execute("SELECT id FROM business_checklist WHERE id = %s", (template_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="清单模板不存在")

        清单名称 = data.get("清单名称")
        触发条件 = data.get("触发条件")
        任务项列表 = data.get("任务项列表")
        是否有效 = data.get("是否有效")
        关联模板ID = data.get("关联模板ID")

        cursor.execute("""
            UPDATE business_checklist
            SET 清单名称 = %s, 触发条件 = %s, 任务项列表 = %s, 是否有效 = %s, 关联模板ID = %s, updated_at = %s
            WHERE id = %s
        """, (清单名称,
              json.dumps(触发条件) if 触发条件 else None,
              json.dumps(任务项列表) if 任务项列表 else None,
              是否有效, 关联模板ID, datetime.now(), template_id))

        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "message": "清单模板更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"更新清单模板失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_checklist_template(template_id: int):
    """删除清单模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否存在
        cursor.execute("SELECT id FROM business_checklist WHERE id = %s", (template_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="清单模板不存在")

        cursor.execute("DELETE FROM business_checklist WHERE id = %s", (template_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "message": "清单模板删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"删除清单模板失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
