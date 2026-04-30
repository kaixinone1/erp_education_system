from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import psycopg2

router = APIRouter(prefix="/api/filter-conditions", tags=["过滤条件管理"])

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DB_CONFIG)


class FilterConditionTemplate(BaseModel):
    id: Optional[int] = None
    category: str
    name: str
    field_name: str
    field_value: str
    filter_condition: str
    sort_order: int = 0
    is_active: bool = True


@router.get("/list")
async def get_filter_conditions():
    """获取所有过滤条件模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, category, name, field_name, field_value, filter_condition, sort_order, is_active
            FROM filter_condition_templates
            WHERE is_active = true
            ORDER BY category, sort_order, id
        """)
        
        rows = cursor.fetchall()
        result = []
        
        for row in rows:
            result.append({
                "id": row[0],
                "category": row[1],
                "name": row[2],
                "field_name": row[3],
                "field_value": row[4],
                "filter_condition": row[5],
                "sort_order": row[6],
                "is_active": row[7]
            })
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"获取过滤条件失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """获取所有类别"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT category
            FROM filter_condition_templates
            WHERE is_active = true
            ORDER BY category
        """)
        
        categories = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": categories}
    except Exception as e:
        print(f"获取类别失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-category/{category}")
async def get_conditions_by_category(category: str):
    """根据类别获取过滤条件"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, category, name, field_name, field_value, filter_condition, sort_order
            FROM filter_condition_templates
            WHERE category = %s AND is_active = true
            ORDER BY sort_order, id
        """, (category,))
        
        rows = cursor.fetchall()
        result = []
        
        for row in rows:
            result.append({
                "id": row[0],
                "category": row[1],
                "name": row[2],
                "field_name": row[3],
                "field_value": row[4],
                "filter_condition": row[5],
                "sort_order": row[6]
            })
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"获取过滤条件失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_filter_condition(condition: FilterConditionTemplate):
    """创建过滤条件"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
            INSERT INTO filter_condition_templates 
            (category, name, field_name, field_value, filter_condition, sort_order, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        params = (
            condition.category,
            condition.name,
            condition.field_name,
            condition.field_value,
            condition.filter_condition,
            condition.sort_order,
            condition.is_active,
            datetime.now(),
            datetime.now()
        )
        
        cursor.execute(sql, params)
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        return {"status": "success", "message": "创建成功", "id": new_id}
    except Exception as e:
        print(f"创建过滤条件失败：{e}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.put("/{condition_id}")
async def update_filter_condition(condition_id: int, condition: FilterConditionTemplate):
    """更新过滤条件"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
            UPDATE filter_condition_templates
            SET category = %s,
                name = %s,
                field_name = %s,
                field_value = %s,
                filter_condition = %s,
                sort_order = %s,
                is_active = %s,
                updated_at = %s
            WHERE id = %s
        """
        
        params = (
            condition.category,
            condition.name,
            condition.field_name,
            condition.field_value,
            condition.filter_condition,
            condition.sort_order,
            condition.is_active,
            datetime.now(),
            condition_id
        )
        
        cursor.execute(sql, params)
        conn.commit()
        
        return {"status": "success", "message": "更新成功"}
    except Exception as e:
        print(f"更新过滤条件失败：{e}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.delete("/{condition_id}")
async def delete_filter_condition(condition_id: int):
    """删除过滤条件（软删除）"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE filter_condition_templates
            SET is_active = false,
                updated_at = %s
            WHERE id = %s
        """, (datetime.now(), condition_id))
        
        conn.commit()
        
        return {"status": "success", "message": "删除成功"}
    except Exception as e:
        print(f"删除过滤条件失败：{e}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
