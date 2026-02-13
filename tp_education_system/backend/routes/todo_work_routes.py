"""
待办工作相关路由
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


@router.get("/list")
async def get_todo_list(status: Optional[str] = None):
    """获取待办工作列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT id, 教师ID, 清单ID, 清单名称, 教师姓名, 
                       任务项列表, 总任务数, 已完成数, 状态, created_at
                FROM todo_work_items 
                WHERE 状态 = %s
                ORDER BY created_at DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT id, 教师ID, 清单ID, 清单名称, 教师姓名, 
                       任务项列表, 总任务数, 已完成数, 状态, created_at
                FROM todo_work_items 
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


@router.get("/{todo_id}")
async def get_todo_detail(todo_id: int):
    """获取待办工作详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, 教师ID, 清单ID, 清单名称, 教师姓名, 
                   任务项列表, 总任务数, 已完成数, 状态, created_at
            FROM todo_work_items 
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
                "created_at": row[9].isoformat() if row[9] else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取待办详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取待办详情失败: {str(e)}")


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
        cursor.execute("SELECT 任务项列表, 总任务数 FROM todo_work_items WHERE id = %s", (todo_id,))
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
            UPDATE todo_work_items 
            SET 任务项列表 = %s, 已完成数 = %s, 状态 = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (json.dumps(task_items), completed_count, new_status, todo_id))
        
        # 如果待办工作已完成，检查是否还有其他待办事项
        if new_status == "completed":
            # 获取教师ID
            cursor.execute("SELECT 教师ID FROM todo_work_items WHERE id = %s", (todo_id,))
            teacher_row = cursor.fetchone()
            if teacher_row and teacher_row[0]:
                teacher_id = teacher_row[0]
                # 检查该教师是否还有其他未完成的待办事项
                cursor.execute("""
                    SELECT COUNT(*) FROM todo_work_items 
                    WHERE 教师ID = %s AND 状态 != 'completed' AND id != %s
                """, (teacher_id, todo_id))
                pending_count = cursor.fetchone()[0]
                
                # 只有所有待办事项都完成后，才删除中间表数据
                if pending_count == 0:
                    cursor.execute("DELETE FROM retirement_report_data WHERE teacher_id = %s", (teacher_id,))
                    print(f"教师 {teacher_id} 的所有待办事项已完成，已删除中间表数据")
                else:
                    print(f"教师 {teacher_id} 还有 {pending_count} 个待办事项未完成，保留中间表数据")
        
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
        
        # 创建待办工作
        total_tasks = len(task_items)
        
        cursor.execute("""
            INSERT INTO todo_work_items 
            (教师ID, 清单ID, 清单名称, 教师姓名, 任务项列表, 总任务数, 已完成数, 状态)
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


@router.get("/checklist/templates")
async def get_checklist_templates():
    """获取所有有效的清单模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, 清单名称, 触发条件, 任务项列表
            FROM business_checklist 
            WHERE 是否有效 = true
            ORDER BY id
        """)
        
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "checklist_name": row[1],
                "trigger_condition": row[2],
                "task_items": row[3]
            })
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        print(f"获取清单模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取清单模板失败: {str(e)}")


@router.post("/auto-summary")
async def auto_summary(data: Dict[str, Any]):
    """自动汇总退休教师绩效工资"""
    try:
        teacher_id = data.get("teacher_id")
        table_name = data.get("table_name")

        if not teacher_id:
            raise HTTPException(status_code=400, detail="缺少教师ID")

        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取教师职务信息
        cursor.execute("""
            SELECT 姓名, 职务 FROM teacher_basic_info WHERE id = %s
        """, (teacher_id,))

        teacher = cursor.fetchone()
        if not teacher:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="教师不存在")

        teacher_name = teacher[0]
        position = teacher[1] or ""

        # 根据职务计算绩效工资（示例逻辑）
        performance_pay = 0
        if "高级" in position:
            performance_pay = 5000
        elif "一级" in position:
            performance_pay = 4000
        elif "二级" in position:
            performance_pay = 3000
        else:
            performance_pay = 2000

        # 将汇总结果写入绩效工资表
        cursor.execute("""
            INSERT INTO performance_pay_approval (教师ID, 教师姓名, 绩效工资, 汇总日期, 备注)
            VALUES (%s, %s, %s, CURRENT_DATE, %s)
            ON CONFLICT (教师ID) DO UPDATE SET
                绩效工资 = EXCLUDED.绩效工资,
                汇总日期 = EXCLUDED.汇总日期,
                备注 = EXCLUDED.备注
        """, (teacher_id, teacher_name, performance_pay, f"根据职务{position}自动汇总"))

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "message": "自动汇总完成",
            "data": {
                "teacher_name": teacher_name,
                "position": position,
                "performance_pay": performance_pay
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"自动汇总失败: {e}")
        raise HTTPException(status_code=500, detail=f"自动汇总失败: {str(e)}")


@router.post("/issue-certificate")
async def issue_certificate(data: Dict[str, Any]):
    """签发退休证"""
    try:
        teacher_id = data.get("teacher_id")
        teacher_name = data.get("teacher_name")
        recipient = data.get("recipient")
        receive_date = data.get("receive_date")

        if not teacher_id or not recipient or not receive_date:
            raise HTTPException(status_code=400, detail="缺少必要参数")

        conn = get_db_connection()
        cursor = conn.cursor()

        # 保存签发记录
        cursor.execute("""
            INSERT INTO retirement_cert_records (教师ID, 教师姓名, 签收人, 签收日期)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (teacher_id, teacher_name, recipient, receive_date))

        record_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "message": "退休证签发记录已保存",
            "record_id": record_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"保存签发记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存签发记录失败: {str(e)}")
