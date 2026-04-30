"""
标签关系管理路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import psycopg2

router = APIRouter(prefix="/api/tag-relations", tags=["tag-relations"])

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


@router.get("/list")
async def get_tag_relations_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    teacher_name: Optional[str] = None,
    id_card: Optional[str] = None,
    tag_id: Optional[int] = None
):
    """获取标签关系列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if teacher_name:
            conditions.append("t.name LIKE %s")
            params.append(f"%{teacher_name}%")
        
        if id_card:
            conditions.append("t.id_card LIKE %s")
            params.append(f"%{id_card}%")
        
        if tag_id:
            conditions.append("r.tag_id = %s")
            params.append(tag_id)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 查询总数
        count_sql = f"""
            SELECT COUNT(*) 
            FROM employee_tag_relations r
            JOIN teacher_basic_info t ON r.employee_id = t.id
            JOIN personal_dict_dictionary d ON r.tag_id = d.id
            WHERE {where_clause}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]
        
        # 查询数据
        offset = (page - 1) * size
        data_sql = f"""
            SELECT 
                r.id,
                r.employee_id,
                t.name as teacher_name,
                t.id_card,
                r.tag_id,
                d.biao_qian as tag_name,
                r.created_at
            FROM employee_tag_relations r
            JOIN teacher_basic_info t ON r.employee_id = t.id
            JOIN personal_dict_dictionary d ON r.tag_id = d.id
            WHERE {where_clause}
            ORDER BY r.id ASC
            LIMIT %s OFFSET %s
        """
        params.extend([size, offset])
        cursor.execute(data_sql, params)
        
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "employee_id": row[1],
                "teacher_name": row[2],
                "id_card": row[3],
                "tag_id": row[4],
                "tag_name": row[5],
                "created_at": row[6].isoformat() if row[6] else None
            })
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": data,
            "total": total,
            "page": page,
            "size": size
        }
        
    except Exception as e:
        print(f"获取标签关系列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.post("")
async def create_tag_relation(data: dict):
    """新增标签关系"""
    try:
        employee_id = data.get("employee_id")
        tag_id = data.get("tag_id")
        
        if not employee_id or not tag_id:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否已存在
        cursor.execute("""
            SELECT id FROM employee_tag_relations 
            WHERE employee_id = %s AND tag_id = %s
        """, (employee_id, tag_id))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="该标签关系已存在")
        
        # 插入新记录
        cursor.execute("""
            INSERT INTO employee_tag_relations (employee_id, tag_id)
            VALUES (%s, %s)
            RETURNING id
        """, (employee_id, tag_id))
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "新增成功",
            "id": new_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"新增标签关系失败: {e}")
        raise HTTPException(status_code=500, detail=f"新增失败: {str(e)}")


@router.put("/{relation_id}")
async def update_tag_relation(relation_id: int, data: dict):
    """编辑标签关系"""
    try:
        employee_id = data.get("employee_id")
        tag_id = data.get("tag_id")
        
        if not employee_id or not tag_id:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查记录是否存在
        cursor.execute("SELECT id FROM employee_tag_relations WHERE id = %s", (relation_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 检查是否与已有记录冲突
        cursor.execute("""
            SELECT id FROM employee_tag_relations 
            WHERE employee_id = %s AND tag_id = %s AND id != %s
        """, (employee_id, tag_id, relation_id))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="该标签关系已存在")
        
        # 更新记录
        cursor.execute("""
            UPDATE employee_tag_relations 
            SET employee_id = %s, tag_id = %s
            WHERE id = %s
        """, (employee_id, tag_id, relation_id))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "编辑成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"编辑标签关系失败: {e}")
        raise HTTPException(status_code=500, detail=f"编辑失败: {str(e)}")


@router.delete("/{relation_id}")
async def delete_tag_relation(relation_id: int):
    """删除标签关系"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM employee_tag_relations WHERE id = %s", (relation_id,))
        conn.commit()
        
        deleted = cursor.rowcount > 0
        
        cursor.close()
        conn.close()
        
        if deleted:
            return {"status": "success", "message": "删除成功"}
        else:
            raise HTTPException(status_code=404, detail="记录不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除标签关系失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/teacher/{teacher_id}/tags")
async def get_teacher_tags(teacher_id: int):
    """获取指定教师的所有标签"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                r.id,
                r.tag_id,
                d.biao_qian as tag_name,
                r.created_at
            FROM employee_tag_relations r
            JOIN personal_dict_dictionary d ON r.tag_id = d.id
            WHERE r.employee_id = %s
            ORDER BY d.biao_qian
        """, (teacher_id,))
        
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "tag_id": row[1],
                "tag_name": row[2],
                "created_at": row[3].isoformat() if row[3] else None
            })
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": data
        }
        
    except Exception as e:
        print(f"获取教师标签失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.post("/save-tags")
async def save_teacher_tags(data: dict):
    """保存教师标签（全量更新）"""
    try:
        employee_id = data.get("employee_id")
        tag_ids = data.get("tag_ids", [])
        
        if not employee_id:
            raise HTTPException(status_code=400, detail="缺少教师ID")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 删除该教师所有现有标签
        cursor.execute("""
            DELETE FROM employee_tag_relations 
            WHERE employee_id = %s
        """, (employee_id,))
        
        # 2. 插入新标签
        if tag_ids:
            for tag_id in tag_ids:
                cursor.execute("""
                    INSERT INTO employee_tag_relations (employee_id, tag_id)
                    VALUES (%s, %s)
                    ON CONFLICT (employee_id, tag_id) DO NOTHING
                """, (employee_id, tag_id))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"成功保存 {len(tag_ids)} 个标签"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"保存教师标签失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.post("/batch-delete")
async def batch_delete_tag_relations(data: dict):
    """批量删除标签关系"""
    try:
        ids = data.get("ids", [])
        
        if not ids:
            raise HTTPException(status_code=400, detail="缺少要删除的ID列表")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 批量删除
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"""
            DELETE FROM employee_tag_relations 
            WHERE id IN ({placeholders})
        """, tuple(ids))
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"成功删除 {deleted_count} 条记录"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"批量删除标签关系失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
