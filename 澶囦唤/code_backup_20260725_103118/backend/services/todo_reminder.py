"""
待办提醒服务
检查待办事项的到期情况，生成提醒并发送消息通知
"""
import logging
from datetime import datetime, timedelta
import psycopg2
from services.message_service import send_todo_reminder, send_overdue_alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def check_deadline_todos():
    """检查待办到期情况，生成提醒并发送消息"""
    logger.info("开始检查待办到期情况...")

    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now().date()
    warning_date = today + timedelta(days=3)  # 3天内到期

    # 1. 检查今日到期的待办
    cursor.execute("""
        SELECT id, title, teacher_name, teacher_id, due_date, status
        FROM todo_items
        WHERE status IN ('pending', 'in_progress')
          AND due_date = %s
    """, (today,))

    today_due = cursor.fetchall()
    for row in today_due:
        logger.info(f"今日到期: {row[1]} - {row[2]}")
        # 发送消息通知
        if row[3] and row[2]:
            send_todo_reminder(row[3], row[2], row[1], str(row[4]))

    # 2. 检查即将到期的待办（3天内）
    cursor.execute("""
        SELECT id, title, teacher_name, teacher_id, due_date, status
        FROM todo_items
        WHERE status IN ('pending', 'in_progress')
          AND due_date > %s
          AND due_date <= %s
    """, (today, warning_date))

    upcoming = cursor.fetchall()
    for row in upcoming:
        logger.info(f"即将到期: {row[1]} - {row[2]} (到期日: {row[3]})")
        # 发送消息通知
        if row[3] and row[2]:
            send_todo_reminder(row[3], row[2], row[1], str(row[4]))

    # 3. 检查已逾期的待办
    cursor.execute("""
        SELECT id, title, teacher_name, teacher_id, due_date, status
        FROM todo_items
        WHERE status IN ('pending', 'in_progress')
          AND due_date < %s
    """, (today,))

    overdue = cursor.fetchall()
    for row in overdue:
        logger.warning(f"已逾期: {row[1]} - {row[2]} (到期日: {row[3]})")
        # 发送逾期警告
        if row[3] and row[2]:
            send_overdue_alert(row[3], row[2], row[1])

    cursor.close()
    conn.close()

    logger.info(f"检查完成: 今日到期 {len(today_due)} 条, 即将到期 {len(upcoming)} 条, 已逾期 {len(overdue)} 条")


def check_overdue_todos():
    """检查逾期待办，生成提醒记录"""
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now().date()

    # 查找已逾期的待办
    cursor.execute("""
        SELECT id, title, teacher_name, due_date
        FROM todo_items
        WHERE status IN ('pending', 'in_progress')
          AND due_date < %s
    """, (today,))

    overdue_todos = cursor.fetchall()

    for todo in overdue_todos:
        # 可以在这里创建逾期提醒记录
        logger.warning(f"逾期待办: ID={todo[0]}, 标题={todo[1]}, 教师={todo[2]}, 到期日={todo[3]}")

    cursor.close()
    conn.close()

    return len(overdue_todos)


def archive_completed_todos():
    """将已完成30天的待办归档到历史表"""
    logger.info("开始归档待办...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 找出已完成超过30天的待办
    archive_date = datetime.now() - timedelta(days=30)
    
    cursor.execute("""
        SELECT id, teacher_id, teacher_name, template_id, business_type, 
               title, description, status, completed_at, created_at, task_items
        FROM todo_items
        WHERE status = 'completed' 
          AND completed_at < %s
    """, (archive_date,))
    
    completed_todos = cursor.fetchall()
    
    archived_count = 0
    for todo in completed_todos:
        # 插入到历史表
        cursor.execute("""
            INSERT INTO todo_history (
                todo_id, teacher_id, teacher_name, template_code, business_type,
                title, description, status, completed_at, created_at, task_items,
                archived_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (
            todo[0], todo[1], todo[2], todo[3], todo[4],
            todo[5], todo[6], todo[7], todo[8], todo[9], todo[10]
        ))
        
        # 从待办表删除
        cursor.execute("DELETE FROM todo_items WHERE id = %s", (todo[0],))
        archived_count += 1
        logger.info(f"已归档: ID={todo[0]}, 标题={todo[5]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"归档完成，共归档 {archived_count} 条待办")
    return archived_count


if __name__ == "__main__":
    print("检查待办到期情况...")
    check_deadline_todos()
    print("检查完成")
