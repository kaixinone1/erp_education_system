#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一待办系统API路由
提供待办管理、触发确认、模板管理等功能
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from datetime import datetime, date
import json

router = APIRouter(prefix="/api/todo-system", tags=["待办系统"])

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )

def get_stats_table_name(business_type):
    """根据业务类型获取对应的统计表名称"""
    business_type_lower = business_type.lower() if business_type else ''
    table_map = {
        'retirement_reminder': 'retirement_reminder_stats',
        'retirement_approval': 'retirement_approval_stats',
        'death_registration': 'death_registration_stats',
        'octogenarian_subsidy': 'octogenarian_subsidy_stats',
        'custom': 'custom_todo_stats'
    }
    return table_map.get(business_type_lower, 'custom_todo_stats')

def update_stats_table(cursor, todo_id, update_data=None):
    """更新对应的统计表"""
    # 先获取待办事项的完整信息
    cursor.execute("""
        SELECT id, business_type, teacher_id, teacher_name,
               created_at, started_at, completed_at, returned_at,
               status, task_items
        FROM todo_items
        WHERE id = %s
    """, (todo_id,))
    todo = cursor.fetchone()
    if not todo:
        return
    
    todo_id, business_type, teacher_id, teacher_name, created_at, started_at, completed_at, returned_at, status, task_items = todo
    
    # 计算任务统计
    if task_items:
        if isinstance(task_items, str):
            task_items = json.loads(task_items)
        total_tasks = len(task_items)
        completed_tasks = sum(1 for t in task_items if t.get('status') == 'completed' or t.get('completed') == True)
        progress = int(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    else:
        total_tasks = 0
        completed_tasks = 0
        progress = 0
    
    # 获取对应的统计表
    table_name = get_stats_table_name(business_type)
    
    # 检查是否已存在记录
    cursor.execute(f"""
        SELECT id FROM {table_name} WHERE todo_item_id = %s
    """, (todo_id,))
    
    if cursor.fetchone():
        # 更新现有记录
        update_fields = []
        params = []
        
        if update_data:
            for key, value in update_data.items():
                if value == 'CURRENT_TIMESTAMP':
                    update_fields.append(f"{key} = CURRENT_TIMESTAMP")
                else:
                    update_fields.append(f"{key} = %s")
                    params.append(value)
        
        # 总是更新这些字段
        update_fields.extend([
            "current_progress = %s",
            "total_tasks = %s",
            "completed_tasks = %s",
            "status = %s",
            "updated_at = CURRENT_TIMESTAMP"
        ])
        params.extend([progress, total_tasks, completed_tasks, status, todo_id])
        
        if update_fields:
            cursor.execute(f"""
                UPDATE {table_name}
                SET {', '.join(update_fields)}
                WHERE todo_item_id = %s
            """, params)
    else:
        # 插入新记录
        cursor.execute(f"""
            INSERT INTO {table_name} (
                todo_item_id, teacher_id, teacher_name,
                create_time, start_process_time, complete_time, return_time,
                current_progress, total_tasks, completed_tasks, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            todo_id, teacher_id, teacher_name,
            created_at, started_at, completed_at, returned_at,
            progress, total_tasks, completed_tasks, status
        ))


class TriggerConfirmRequest(BaseModel):
    trigger_id: int
    confirmed: bool
    notes: Optional[str] = None


class CreateCustomTodoRequest(BaseModel):
    creator: str
    title: str
    description: Optional[str] = None
    plan_date: Optional[date] = None
    remind_days: Optional[int] = 3
    related_teacher_id: Optional[int] = None
    related_teacher_name: Optional[str] = None


@router.get("/pending-triggers")
async def get_pending_triggers(
    status: Optional[str] = Query(None, description="筛选状态: pending/confirmed/ignored"),
    business_type: Optional[str] = Query(None, description="业务类型筛选")
):
    """
    获取待确认的触发事件列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            SELECT pt.id, pt.template_code, pt.teacher_id, pt.teacher_name,
                   pt.trigger_reason, pt.status,
                   pt.created_at, pt.handle_time, pt.handle_note
            FROM pending_triggers pt
            WHERE 1=1
        """
        params = []
        
        if status:
            sql += " AND pt.status = %s"
            params.append(status)
        
        if business_type:
            sql += " AND pt.trigger_reason LIKE %s"
            params.append(f'%{business_type}%')
        
        sql += " ORDER BY pt.created_at DESC"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        triggers = []
        for row in rows:
            triggers.append({
                "id": row[0],
                "template_code": row[1],
                "teacher_id": row[2],
                "teacher_name": row[3],
                "trigger_reason": row[4],
                "status": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "handle_time": row[7].isoformat() if row[7] else None,
                "handle_note": row[8]
            })
        
        return {"success": True, "data": triggers}
    
    finally:
        cursor.close()
        conn.close()


@router.get("/todo-history")
async def get_todo_history(
    teacher_name: str = None,
    business_type: str = None,
    status: str = None,
    page: int = 1,
    size: int = 20
):
    """
    获取待办历史记录
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            SELECT id, todo_id, teacher_id, teacher_name, template_code, business_type,
                   title, description, status, completed_at, created_at, archived_at,
                   return_count, return_reason, notes, task_items
            FROM todo_history
            WHERE 1=1
        """
        params = []
        
        if teacher_name:
            sql += " AND teacher_name LIKE %s"
            params.append(f'%{teacher_name}%')
        
        if business_type:
            sql += " AND business_type = %s"
            params.append(business_type)
        
        if status:
            sql += " AND status = %s"
            params.append(status)
        
        # 获取总数
        count_sql = "SELECT COUNT(*) FROM (" + sql + ") AS sub"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]
        
        # 分页查询
        sql += " ORDER BY todo_id, created_at DESC LIMIT %s OFFSET %s"
        params.extend([size, (page - 1) * size])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        history_list = []
        for row in rows:
            notes_data = row[14]
            if isinstance(notes_data, str):
                try:
                    notes_data = json.loads(notes_data)
                except:
                    notes_data = []
            
            task_items_data = row[15]
            if isinstance(task_items_data, str):
                try:
                    task_items_data = json.loads(task_items_data)
                except:
                    task_items_data = []
            
            history_list.append({
                "id": row[0],
                "todo_id": row[1],
                "teacher_id": row[2],
                "teacher_name": row[3],
                "template_code": row[4],
                "business_type": row[5],
                "title": row[6],
                "description": row[7],
                "status": row[8],
                "completed_at": row[9].isoformat() if row[9] else None,
                "created_at": row[10].isoformat() if row[10] else None,
                "archived_at": row[11].isoformat() if row[11] else None,
                "return_count": row[12] or 0,
                "return_reason": row[13],
                "notes": notes_data if notes_data else [],
                "task_items": task_items_data if task_items_data else []
            })
        
        return {
            "success": True,
            "data": history_list,
            "total": total,
            "page": page,
            "size": size
        }
    
    finally:
        cursor.close()
        conn.close()


@router.post("/confirm-trigger")
async def confirm_trigger(request: TriggerConfirmRequest):
    """
    确认或忽略触发事件
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 更新触发事件状态
        cursor.execute("""
            UPDATE pending_triggers
            SET status = %s,
                handle_time = CURRENT_TIMESTAMP,
                handle_note = %s
            WHERE id = %s
            RETURNING template_code, teacher_id, teacher_name, trigger_reason
        """, ("confirmed" if request.confirmed else "ignored", request.notes, request.trigger_id))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="触发事件不存在")
        
        template_code, teacher_id, teacher_name, trigger_reason = row
        
        # 如果确认，则创建待办事项
        if request.confirmed and template_code:
            # 直接使用pending_triggers中的template_code
                
                # 获取模板详情
                cursor.execute("""
                    SELECT template_name, task_flow, due_date_rule
                    FROM todo_templates
                    WHERE template_code = %s
                """, (template_code,))
                template_detail = cursor.fetchone()
                
                if template_detail:
                    template_name, task_flow, due_date_rule = template_detail
                    
                    # 计算截止日期
                    due_date = None
                    if due_date_rule:
                        # 简单处理：如果是数字，表示天数
                        try:
                            days = int(due_date_rule)
                            from datetime import timedelta
                            due_date = date.today() + timedelta(days=days)
                        except:
                            pass
                    
                    # 创建待办事项
                    cursor.execute("""
                        INSERT INTO todo_items (
                            template_id, business_type, teacher_id, teacher_name,
                            title, description, status, priority, due_date,
                            task_items, created_by
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        template_code,
                        template_code.lower().replace('_', ''),
                        teacher_id,
                        teacher_name,
                        f"{teacher_name} - {template_name}",
                        f"由触发条件自动创建的待办事项",
                        "pending",
                        "normal",
                        due_date,
                        json.dumps(task_flow) if task_flow else None,
                        "system"
                    ))
                    
                    todo_id = cursor.fetchone()[0]
                    
                    # 同步创建统计记录
                    update_stats_table(cursor, todo_id)
                    
                    # 创建待办历史记录
                    cursor.execute("""
                        INSERT INTO todo_history (
                            todo_id, teacher_id, teacher_name, template_code, business_type,
                            title, description, status, task_items, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """, (
                        todo_id, teacher_id, teacher_name, template_code,
                        template_code.lower().replace('_', ''),
                        f"{teacher_name} - {template_name}",
                        f"由触发条件自动创建的待办事项",
                        "pending",
                        json.dumps(task_flow) if task_flow else None
                    ))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "已确认" if request.confirmed else "已忽略",
            "todo_created": request.confirmed
        }
    
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()


@router.get("/todo-list")
async def get_todo_list(
    status: Optional[str] = Query(None, description="状态筛选: pending/in_progress/completed"),
    business_type: Optional[str] = Query(None, description="业务类型筛选")
):
    """
    获取待办事项列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 先检查并更新已完成状态（进度100%自动变completed）
        cursor.execute("""
            SELECT id, task_items FROM todo_items WHERE status = 'pending'
        """)
        for row in cursor.fetchall():
            todo_id = row[0]
            task_items = row[1]
            if task_items:
                if isinstance(task_items, str):
                    try:
                        task_items = json.loads(task_items)
                    except:
                        task_items = []
                total = len(task_items) if task_items else 0
                completed = sum(1 for t in task_items if t.get('completed')) if task_items else 0
                if total > 0 and completed == total:
                    # 自动更新为已完成
                    cursor.execute("""
                        UPDATE todo_items 
                        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (todo_id,))
        
        conn.commit()
        
        sql = """
            SELECT id, template_id, business_type, teacher_id, teacher_name,
                   title, description, status, priority, due_date,
                   task_items, created_by, created_at, completed_at
            FROM todo_items
            WHERE 1=1
        """
        params = []
        
        if status:
            sql += " AND status = %s"
            params.append(status)
        
        if business_type:
            sql += " AND business_type = %s"
            params.append(business_type)
        
        # 排序规则：
        # 1. 待处理(pending)放在最上面
        # 2. 按业务类型分类（template_id）
        # 3. 待处理按创建时间正序（最早的在前）
        # 4. 已完成的放在下面，按完成时间倒序（最新完成的在前）
        sql += " ORDER BY status DESC, template_id, CASE WHEN status = 'pending' THEN created_at END ASC, CASE WHEN status = 'completed' THEN completed_at END DESC"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # 查询模板名称映射 (template_code -> template_name)
        cursor.execute("SELECT template_code, template_name FROM todo_templates")
        template_map = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 查询模板ID到模板代码的映射 (template_id -> template_code)
        cursor.execute("SELECT id, template_code FROM todo_templates")
        template_id_to_code = {row[0]: row[1] for row in cursor.fetchall()}
        
        todos = []
        for row in rows:
            task_items = row[10]
            if isinstance(task_items, str):
                try:
                    task_items = json.loads(task_items)
                except:
                    task_items = []
            
            # 计算任务统计
            total_tasks = len(task_items) if task_items else 0
            completed_tasks = sum(1 for t in task_items if t.get('completed') or t.get('完成状态')) if task_items else 0
            progress = int(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            template_id = row[1]
            # 如果template_id是字符串（如'MIGRATED_4'），直接作为template_code使用
            if isinstance(template_id, str):
                template_code = template_id
            else:
                template_code = template_id_to_code.get(template_id, '')
            template_name = template_map.get(template_code, '待办任务')
            business_type = row[2]
            
            # 根据业务类型显示中文名称
            business_type_lower = business_type.lower() if business_type else ''
            business_type_display = {
                'retirement_reminder': '到龄退休提醒',
                'octogenarian_subsidy': '80周岁高龄补贴申请',
                'death_registration': '死亡登记',
                'custom': '自定义待办'
            }.get(business_type_lower, template_name)
            
            todos.append({
                "id": row[0],
                "template_id": template_id,
                "template_code": template_code,
                "template_name": template_name,
                "business_type": business_type,
                "business_type_display": business_type_display,
                "teacher_id": row[3],
                "teacher_name": row[4],
                "title": row[5],
                "description": row[6],
                "status": row[7],
                "priority": row[8],
                "due_date": row[9].isoformat() if row[9] else None,
                "task_items": task_items,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "progress": progress,
                "created_by": row[11],
                "created_at": row[12].isoformat() if row[12] else None,
                "completed_at": row[13].isoformat() if row[13] else None
            })
        
        return {"success": True, "data": todos}
    
    finally:
        cursor.close()
        conn.close()


@router.post("/todo/{todo_id}/start")
async def start_todo(todo_id: int):
    """
    开始处理待办
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE todo_items
            SET status = 'in_progress', started_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'pending'
            RETURNING id
        """, (todo_id,))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="待办不存在或状态不正确")
        
        # 同步更新统计表
        update_stats_table(cursor, todo_id, {
            'start_process_time': 'CURRENT_TIMESTAMP'
        })
        
        conn.commit()
        return {"success": True, "message": "已开始处理"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.post("/todo/{todo_id}/complete")
async def complete_todo(todo_id: int):
    """
    完成待办
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE todo_items
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'in_progress'
            RETURNING id
        """, (todo_id,))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="待办不存在或状态不正确")
        
        # 同步更新统计表
        update_stats_table(cursor, todo_id, {
            'complete_time': 'CURRENT_TIMESTAMP'
        })
        
        conn.commit()
        return {"success": True, "message": "已完成"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.post("/todo/{todo_id}/return")
async def return_todo(todo_id: int, data: dict = Body(...)):
    """
    退回待办 - 退回后重置任务清单，从0开始重新办理
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        reason = data.get('reason', '')
        
        # 先获取当前待办的任务清单
        cursor.execute("""
            SELECT task_items FROM todo_items WHERE id = %s
        """, (todo_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="待办不存在")
        
        task_items = row[0]
        # 重置所有任务项为未完成状态
        if task_items:
            if isinstance(task_items, str):
                task_items = json.loads(task_items)
            # 将所有任务项重置为未完成
            for task in task_items:
                task['completed'] = False
                task['status'] = 'pending'
                if 'completed_at' in task:
                    del task['completed_at']
                if 'completed_by' in task:
                    del task['completed_by']
        
        cursor.execute("""
            UPDATE todo_items
            SET status = 'pending', 
                returned_at = CURRENT_TIMESTAMP,
                return_reason = %s,
                task_items = %s,
                completed_at = NULL
            WHERE id = %s
            RETURNING id
        """, (reason, json.dumps(task_items) if task_items else None, todo_id))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="待办不存在")
        
        # 同步更新统计表
        update_stats_table(cursor, todo_id, {
            'return_time': 'CURRENT_TIMESTAMP',
            'return_reason': reason
        })
        
        conn.commit()
        return {"success": True, "message": "已退回，请重新办理"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.get("/templates")
async def get_templates():
    """
    获取所有清单模板
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, template_code, template_name, business_type,
                   description, due_date_rule, is_enabled
            FROM todo_templates
            ORDER BY id
        """)
        
        rows = cursor.fetchall()
        
        templates = []
        for row in rows:
            templates.append({
                "id": row[0],
                "template_code": row[1],
                "template_name": row[2],
                "business_type": row[3],
                "description": row[4],
                "due_date_rule": row[5],
                "is_enabled": row[6]
            })
        
        return {"success": True, "data": templates}
    
    finally:
        cursor.close()
        conn.close()


@router.get("/trigger-conditions")
async def get_trigger_conditions():
    """
    获取所有触发条件
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, condition_name, listen_table, listen_field,
                   trigger_type, trigger_value, template_code, is_enabled, description
            FROM trigger_conditions
            ORDER BY id
        """)
        
        rows = cursor.fetchall()
        
        conditions = []
        for row in rows:
            conditions.append({
                "id": row[0],
                "condition_name": row[1],
                "listen_table": row[2],
                "listen_field": row[3],
                "trigger_type": row[4],
                "trigger_value": row[5],
                "template_code": row[6],
                "is_enabled": row[7],
                "description": row[8]
            })
        
        return {"success": True, "data": conditions}
    
    finally:
        cursor.close()
        conn.close()


@router.post("/custom-todo")
async def create_custom_todo(request: CreateCustomTodoRequest):
    """
    创建用户自定义待办
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO user_custom_todos (
                creator, title, description, plan_date,
                remind_days, related_teacher_id, related_teacher_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            request.creator,
            request.title,
            request.description,
            request.plan_date,
            request.remind_days,
            request.related_teacher_id,
            request.related_teacher_name
        ))
        
        todo_id = cursor.fetchone()[0]
        conn.commit()
        
        return {
            "success": True,
            "message": "自定义待办创建成功",
            "todo_id": todo_id
        }
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()


@router.get("/stats")
async def get_todo_stats():
    """
    获取待办统计
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # 待办数量统计
        cursor.execute("""
            SELECT status, COUNT(*) FROM todo_items GROUP BY status
        """)
        stats['todo_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 待确认触发数量
        cursor.execute("""
            SELECT status, COUNT(*) FROM pending_triggers GROUP BY status
        """)
        stats['trigger_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 业务类型分布
        cursor.execute("""
            SELECT business_type, COUNT(*) FROM todo_items GROUP BY business_type
        """)
        stats['business_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {"success": True, "data": stats}
    
    finally:
        cursor.close()
        conn.close()


# ==================== 新增：任务状态更新和办理记录API ====================

from fastapi import Body


@router.post("/todo/{todo_id}/update-task-status")
async def update_task_status(todo_id: int, data: dict = Body(...)):
    """
    更新待办任务项的完成状态
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        task_index = data.get("task_index")
        completed = data.get("completed", False)
        
        if task_index is None:
            raise HTTPException(status_code=400, detail="缺少task_index参数")
        
        # 获取当前任务列表
        cursor.execute("""
            SELECT task_items FROM todo_items WHERE id = %s
        """, (todo_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="待办事项不存在")
        
        task_items = row[0]
        if isinstance(task_items, str):
            try:
                task_items = json.loads(task_items)
            except:
                task_items = []
        
        if not task_items or task_index >= len(task_items):
            raise HTTPException(status_code=400, detail="任务索引无效")
        
        # 更新任务完成状态
        task_items[task_index]["completed"] = completed
        task_items[task_index]["完成状态"] = completed
        if completed:
            from datetime import datetime
            task_items[task_index]["完成时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 计算已完成数
        completed_count = sum(1 for t in task_items if t.get("completed") or t.get("完成状态"))
        total_count = len(task_items)
        
        # 更新状态
        new_status = "completed" if completed_count >= total_count else "pending"
        
        cursor.execute("""
            UPDATE todo_items 
            SET task_items = %s, status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (json.dumps(task_items), new_status, todo_id))
        
        # 同步更新统计表
        update_stats_table(cursor, todo_id)
        
        # 记录到待办历史（记录每次任务项完成情况）
        task_title = task_items[task_index].get("标题") or task_items[task_index].get("name", f"任务{task_index+1}")
        action = "完成" if completed else "取消完成"
        
        # 获取当前办理记录
        cursor.execute("""
            SELECT notes FROM todo_items WHERE id = %s
        """, (todo_id,))
        row = cursor.fetchone()
        notes = []
        if row and row[0]:
            if isinstance(row[0], str):
                try:
                    notes = json.loads(row[0])
                except:
                    notes = []
            else:
                notes = row[0] if row[0] else []
        
        # 添加办理记录
        from datetime import datetime
        notes.append({
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "事项": f"{task_title} - {action}"
        })
        
        # 更新待办事项的notes
        cursor.execute("""
            UPDATE todo_items 
            SET notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (json.dumps(notes), todo_id))
        
        # 更新待办历史的notes和task_items
        cursor.execute("""
            UPDATE todo_history 
            SET notes = %s,
                task_items = %s, 
                status = %s,
                completed_at = CASE WHEN %s = 'completed' THEN CURRENT_TIMESTAMP ELSE completed_at END
            WHERE todo_id = %s
        """, (json.dumps(notes), json.dumps(task_items), new_status, new_status, todo_id))
        
        conn.commit()
        
        return {
            "status": "success",
            "message": "任务状态更新成功",
            "completed_tasks": completed_count,
            "total_tasks": total_count
        }
    
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新任务状态失败: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()


@router.get("/todo/{todo_id}/notes")
async def get_todo_notes(todo_id: int):
    """
    获取待办事项的办理记录
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT notes FROM todo_items WHERE id = %s
        """, (todo_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="待办事项不存在")
        
        notes = row[0]
        if isinstance(notes, str):
            try:
                notes = json.loads(notes)
            except:
                notes = []
        
        return {
            "status": "success",
            "data": {
                "todo_id": todo_id,
                "notes": notes if notes else []
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取办理记录失败: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()


@router.post("/todo/{todo_id}/notes")
async def update_todo_notes(todo_id: int, data: dict = Body(...)):
    """
    更新待办事项的办理记录
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        notes = data.get("notes", [])
        
        cursor.execute("""
            UPDATE todo_items 
            SET notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (json.dumps(notes), todo_id))
        
        conn.commit()
        
        return {
            "status": "success",
            "message": "办理记录保存成功"
        }
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"保存办理记录失败: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()


@router.get("/check-delayed-retirement/{teacher_id}")
async def check_delayed_retirement(teacher_id: int):
    """
    检查教师是否在延迟退休教师表中
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, 姓名, 批准日期, 退休年龄
            FROM delayed_retirement_records
            WHERE 教师id = %s
        """, (teacher_id,))
        
        row = cursor.fetchone()
        
        if row:
            return {
                "status": "success",
                "exists": True,
                "data": {
                    "id": row[0],
                    "姓名": row[1],
                    "批准日期": row[2].isoformat() if row[2] else None,
                    "退休年龄": row[3]
                }
            }
        else:
            return {
                "status": "success",
                "exists": False,
                "data": None
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()
