"""
标签关系管理路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import json
import psycopg2

router = APIRouter(prefix="/api/tag-relations", tags=["tag-relations"])

# ==================== 标签分类规则配置 ====================
# 五类标签定义：每类标签有不同的选择规则（多选/单选/互斥/条件）
TAG_CATEGORIES = [
    {
        "category": "工资类",
        "description": "工资构成标签，可多选",
        "selection_type": "multi",  # 多选
        "tag_ids": [1, 2, 3, 4],  # 基础工资、绩效工资、乡镇补贴、岗位聘用
    },
    {
        "category": "编制类",
        "description": "编制类型，仅新机制教师可勾选",
        "selection_type": "conditional",  # 条件勾选
        "tag_ids": [5],  # 新机制
        "condition": "新机制教师专用，非新机制教师禁止勾选",
    },
    {
        "category": "政治面貌类",
        "description": "政治面貌标签，互斥选择",
        "selection_type": "multi",  # 平铺展示，互斥
        "tag_ids": [11, 12, 13, 14, 15, 16],  # gcdy、dj、组织关系挂靠、gqty、tj、群众
        "mutual_exclusive": True,  # 互斥：勾选一个自动取消其他
    },
    {
        "category": "任职状态类",
        "description": "任职状态标签，互斥单选",
        "selection_type": "single",  # 单选互斥
        "tag_ids": [17, 18, 19, 20, 21, 22, 23, 24, 25],  # 在职、调出、调离、辞职、借调、离休、退休、去世、病休
        "mutual_exclusive": True,
    },
    {
        "category": "请长假类",
        "description": "因病请长假可勾选",
        "selection_type": "conditional",  # 条件勾选
        "tag_ids": [26],  # 病假
        "condition": "因病请长假可勾选",
    },
    {
        "category": "其他业务类",
        "description": "其他业务相关标签",
        "selection_type": "multi",  # 多选
        "tag_ids": [6, 7, 8, 9, 10],  # 年度考核、人事年报、工资年报、乡村定向、延迟退休
    },
]

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

# 标签关系表可筛选字段映射（前端字段名 → SQL列引用）
TAG_FILTER_FIELD_MAP = {
    "teacher_name": 't."姓名"',
    "id_card": 't."身份证号码"',
    "tag_name": "d.biao_qian",
    "tag_id": "r.tag_id",
    "employee_id": "r.employee_id",
}


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


@router.get("/list")
async def get_tag_relations_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=10000),
    teacher_name: Optional[str] = None,
    id_card: Optional[str] = None,
    tag_id: Optional[int] = None,
    keyword: Optional[str] = None,
    filter: Optional[str] = None
):
    """获取标签关系列表（支持新旧两种筛选格式）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        # 新格式：条件数组 [{field, operator, value}, ...]（优先处理）
        if filter:
            try:
                filter_data = json.loads(filter)
                if isinstance(filter_data, list):
                    for cond in filter_data:
                        field = cond.get('field', '')
                        operator = cond.get('operator', 'contains')
                        value = cond.get('value', '')
                        
                        if not field or field not in TAG_FILTER_FIELD_MAP:
                            continue
                        
                        col_ref = TAG_FILTER_FIELD_MAP[field]
                        param_name = f"filter_{field}_{len(params)}"
                        
                        if operator == 'is_null':
                            conditions.append(f"{col_ref} IS NULL")
                        elif operator == 'is_not_null':
                            conditions.append(f"{col_ref} IS NOT NULL")
                        elif operator == 'eq':
                            conditions.append(f"CAST({col_ref} AS TEXT) = %s")
                            params.append(str(value))
                        elif operator == 'neq':
                            conditions.append(f"CAST({col_ref} AS TEXT) != %s")
                            params.append(str(value))
                        elif operator == 'contains':
                            conditions.append(f"CAST({col_ref} AS TEXT) ILIKE %s")
                            params.append(f"%{value}%")
                        elif operator == 'not_contains':
                            conditions.append(f"CAST({col_ref} AS TEXT) NOT ILIKE %s")
                            params.append(f"%{value}%")
                        elif operator == 'starts_with':
                            conditions.append(f"CAST({col_ref} AS TEXT) ILIKE %s")
                            params.append(f"{value}%")
                        elif operator == 'ends_with':
                            conditions.append(f"CAST({col_ref} AS TEXT) ILIKE %s")
                            params.append(f"%{value}")
                        elif operator == 'gt':
                            conditions.append(f"CAST({col_ref} AS TEXT) > %s")
                            params.append(str(value))
                        elif operator == 'gte':
                            conditions.append(f"CAST({col_ref} AS TEXT) >= %s")
                            params.append(str(value))
                        elif operator == 'lt':
                            conditions.append(f"CAST({col_ref} AS TEXT) < %s")
                            params.append(str(value))
                        elif operator == 'lte':
                            conditions.append(f"CAST({col_ref} AS TEXT) <= %s")
                            params.append(str(value))
            except json.JSONDecodeError:
                pass
        
        # 旧格式兼容：独立参数
        if teacher_name:
            conditions.append('t."姓名" LIKE %s')
            params.append(f"%{teacher_name}%")
        
        if id_card:
            conditions.append('t."身份证号码" LIKE %s')
            params.append(f"%{id_card}%")
        
        if tag_id:
            conditions.append("r.tag_id = %s")
            params.append(tag_id)
        
        if keyword:
            keyword_conditions = []
            keyword_conditions.append('t."姓名" LIKE %s')
            params.append(f"%{keyword}%")
            keyword_conditions.append('t."身份证号码" LIKE %s')
            params.append(f"%{keyword}%")
            keyword_conditions.append("d.biao_qian LIKE %s")
            params.append(f"%{keyword}%")
            conditions.append("(" + " OR ".join(keyword_conditions) + ")")
        
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
                t."姓名" as teacher_name,
                t."身份证号码",
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
    """保存教师标签（全量更新，含互斥规则校验）"""
    try:
        employee_id = data.get("employee_id")
        tag_ids = data.get("tag_ids", [])
        
        if not employee_id:
            raise HTTPException(status_code=400, detail="缺少教师ID")
        
        # 验证互斥规则
        validation_error = _validate_tag_mutual_exclusion(tag_ids)
        if validation_error:
            raise HTTPException(status_code=400, detail=validation_error)
        
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


@router.get("/categories")
async def get_tag_categories():
    """获取标签分类规则（供前端标签选择区域使用）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有标签的名称
        cursor.execute("SELECT id, biao_qian FROM personal_dict_dictionary ORDER BY id")
        all_tags = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        conn.close()
        
        # 构建分类数据，填充标签名称
        categories = []
        for cat in TAG_CATEGORIES:
            cat_data = {
                "category": cat["category"],
                "description": cat.get("description", ""),
                "selection_type": cat["selection_type"],
                "condition": cat.get("condition", ""),
            }
            
            if cat["selection_type"] == "mutual_exclusive_groups":
                # 分组互斥类型（已废弃，保留兼容）
                groups = []
                for g in cat["groups"]:
                    group_data = {
                        "group_name": g["group_name"],
                        "selection_type": g["selection_type"],
                        "tags": [{"id": tid, "name": all_tags.get(tid, f"未知标签{tid}")} for tid in g["tag_ids"]],
                    }
                    groups.append(group_data)
                cat_data["groups"] = groups
                cat_data["mutual_exclusive"] = cat.get("mutual_exclusive", False)
            else:
                # 普通类型（multi/single/conditional）
                cat_data["tags"] = [{"id": tid, "name": all_tags.get(tid, f"未知标签{tid}")} for tid in cat["tag_ids"]]
                cat_data["mutual_exclusive"] = cat.get("mutual_exclusive", False)
            
            categories.append(cat_data)
        
        return {
            "status": "success",
            "data": categories
        }
    except Exception as e:
        print(f"获取标签分类失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


def _validate_tag_mutual_exclusion(tag_ids: list) -> Optional[str]:
    """验证标签互斥规则，返回错误信息或None（验证通过）"""
    
    # 构建 tag_id -> category 的映射
    tag_category_map = {}
    for cat in TAG_CATEGORIES:
        for tid in cat.get("tag_ids", []):
            tag_category_map[tid] = (cat["category"], None)
    
    # 检查任职状态类互斥（单选）
    status_tag_ids = {17, 18, 19, 20, 21, 22, 23, 24, 25}
    selected_status = [tid for tid in tag_ids if tid in status_tag_ids]
    if len(selected_status) > 1:
        return "任职状态类标签只能选择一个"
    
    # 检查政治面貌类互斥（平铺，勾选一个自动取消其他）
    political_tag_ids = {11, 12, 13, 14, 15, 16}
    selected_political = [tid for tid in tag_ids if tid in political_tag_ids]
    if len(selected_political) > 1:
        return "政治面貌类标签互斥，只能选择一个"
    
    return None
