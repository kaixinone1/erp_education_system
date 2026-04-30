"""
待办工作相关路由 - 使用原来的中文字段名
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import psycopg2
from datetime import datetime
import json

router = APIRouter(prefix="/api/todo-work", tags=["todo-work"])

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


@router.get("/count")
async def get_todo_count():
    """获取待办工作数量"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 统计未完成或进行中的待办工作数量
        cursor.execute("""
            SELECT COUNT(*) FROM todo_work 
            WHERE 状态 IN ('待处理', '进行中', 'pending')
        """)
        
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "count": count
        }
    except Exception as e:
        print(f"获取待办数量失败: {e}")
        return {
            "status": "error",
            "count": 0,
            "message": str(e)
        }


@router.get("/list")
async def get_todo_list(status: Optional[str] = None):
    """获取待办工作列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 使用原来的中文字段名查询 todo_work 表
        if status:
            cursor.execute("""
                SELECT id, 教师id, 清单id, 清单名称, 教师姓名, 
                       任务项列表, 总任务数, 已完成数, 状态, created_at
                FROM todo_work 
                WHERE 状态 = %s
                ORDER BY created_at DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT id, 教师id, 清单id, 清单名称, 教师姓名, 
                       任务项列表, 总任务数, 已完成数, 状态, created_at
                FROM todo_work 
                ORDER BY created_at DESC
            """)
        
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "teacher_id": row[1],
                "checklist_id": row[2],
                "checklist_name": row[3],
                "teacher_name": row[4],
                "task_items": row[5],
                "total_tasks": row[6],
                "completed_tasks": row[7],
                "status": row[8],
                "created_at": row[9].isoformat() if row[9] else None
            })
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        print(f"获取待办列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取待办列表失败: {str(e)}")


@router.post("/update-status")
async def update_task_status(data: Dict[str, Any]):
    """更新任务完成状态"""
    try:
        todo_id = data.get("todo_id")
        task_index = data.get("task_index")
        completed = data.get("completed", False)
        
        if todo_id is None or task_index is None:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取当前任务列表
        cursor.execute("SELECT 任务项列表, 总任务数 FROM todo_work WHERE id = %s", (todo_id,))
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="待办工作不存在")
        
        task_items = row[0] if isinstance(row[0], list) else json.loads(row[0]) if row[0] else []
        total_tasks = row[1] or len(task_items)
        
        # 更新指定任务的完成状态
        if 0 <= task_index < len(task_items):
            task_items[task_index]["完成状态"] = completed
        
        # 计算已完成数
        completed_count = sum(1 for task in task_items if task.get("完成状态", False))
        
        # 更新状态
        new_status = "completed" if completed_count >= total_tasks else "pending"
        
        cursor.execute("""
            UPDATE todo_work 
            SET 任务项列表 = %s, 已完成数 = %s, 状态 = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (json.dumps(task_items), completed_count, new_status, todo_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "任务状态更新成功",
            "completed_tasks": completed_count,
            "total_tasks": total_tasks
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新任务状态失败: {str(e)}")


@router.post("/create-from-checklist")
async def create_todo_from_checklist(data: Dict[str, Any]):
    """从清单模板创建待办工作"""
    try:
        teacher_id = data.get("teacher_id")
        teacher_name = data.get("teacher_name")
        checklist_id = data.get("checklist_id")
        
        if not teacher_id or not checklist_id:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取清单模板
        cursor.execute("""
            SELECT 清单名称, 任务项列表 
            FROM business_checklist 
            WHERE id = %s AND 是否有效 = true
        """, (checklist_id,))
        
        checklist = cursor.fetchone()
        if not checklist:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="清单模板不存在或已禁用")
        
        checklist_name = checklist[0]
        task_items = checklist[1] if isinstance(checklist[1], list) else json.loads(checklist[1]) if checklist[1] else []
        
        # 确保至少有一个任务项（如果没有，添加默认的"确认完成"项）
        if not task_items or len(task_items) == 0:
            task_items = [{
                "标题": "确认完成",
                "说明": f"请确认{teacher_name}的'{checklist_name}'已处理完毕",
                "类型": "确认",
                "完成状态": False
            }]
        
        # 创建待办工作
        total_tasks = len(task_items)
        
        cursor.execute("""
            INSERT INTO todo_work 
            (教师id, 清单id, 清单名称, 教师姓名, 任务项列表, 总任务数, 已完成数, 状态)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            teacher_id,
            checklist_id,
            checklist_name,
            teacher_name,
            json.dumps(task_items),
            total_tasks,
            0,
            "pending"
        ))
        
        todo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "待办工作创建成功",
            "todo_id": todo_id,
            "checklist_name": checklist_name,
            "total_tasks": total_tasks
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建待办工作失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建待办工作失败: {str(e)}")


@router.post("/update-notes")
async def update_todo_notes(data: Dict[str, Any]):
    """更新待办工作的办理记录"""
    try:
        todo_id = data.get("todo_id")
        notes = data.get("notes", [])
        
        if todo_id is None:
            raise HTTPException(status_code=400, detail="缺少todo_id参数")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查待办是否存在
        cursor.execute("SELECT id FROM todo_work WHERE id = %s", (todo_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="待办工作不存在")
        
        # 更新办理记录
        cursor.execute("""
            UPDATE todo_work 
            SET notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (json.dumps(notes, ensure_ascii=False), todo_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "办理记录保存成功",
            "notes_count": len(notes) if notes else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"保存办理记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存办理记录失败: {str(e)}")


# 注意：这个路由必须放在最后，因为它会匹配任何路径
@router.get("/{todo_id}")
async def get_todo_detail(todo_id: int):
    """获取待办工作详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, 教师id, 清单id, 清单名称, 教师姓名, 
                   任务项列表, 总任务数, 已完成数, 状态, created_at, notes
            FROM todo_work 
            WHERE id = %s
        """, (todo_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="待办工作不存在")
        
        return {
            "status": "success",
            "data": {
                "id": row[0],
                "teacher_id": row[1],
                "checklist_id": row[2],
                "checklist_name": row[3],
                "teacher_name": row[4],
                "task_items": row[5],
                "total_tasks": row[6],
                "completed_tasks": row[7],
                "status": row[8],
                "created_at": row[9].isoformat() if row[9] else None,
                "notes": row[10] if len(row) > 10 else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取待办详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取待办详情失败: {str(e)}")
