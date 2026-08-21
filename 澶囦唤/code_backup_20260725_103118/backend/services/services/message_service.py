"""
消息通知服务
支持待办事项的站内消息通知
"""
import logging
from datetime import datetime
from typing import List, Optional
import psycopg2

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


class MessageService:
    """消息服务"""

    @staticmethod
    def create_message(
        user_id: int,
        title: str,
        content: str,
        message_type: str = "info",
        related_type: str = None,
        related_id: int = None
    ) -> int:
        """创建消息"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO system_messages (user_id, title, content, message_type, related_type, related_id, is_read, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, false, %s)
            RETURNING id
        """, (user_id, title, content, message_type, related_type, related_id, datetime.now()))

        message_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"创建消息: ID={message_id}, 用户={user_id}, 标题={title}")
        return message_id

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """获取未读消息数量"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM system_messages
            WHERE user_id = %s AND is_read = false
        """, (user_id,))

        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return count

    @staticmethod
    def get_messages(user_id: int, limit: int = 20, offset: int = 0) -> List[dict]:
        """获取消息列表"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, content, message_type, related_type, related_id, is_read, created_at
            FROM system_messages
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "message_type": row[3],
                "related_type": row[4],
                "related_id": row[5],
                "is_read": row[6],
                "created_at": row[7]
            })

        cursor.close()
        conn.close()

        return messages

    @staticmethod
    def mark_as_read(message_id: int, user_id: int) -> bool:
        """标记消息为已读"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE system_messages
            SET is_read = true
            WHERE id = %s AND user_id = %s
        """, (message_id, user_id))

        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        return affected > 0


def send_todo_reminder(teacher_id: int, teacher_name: str, todo_title: str, due_date: str):
    """发送待办提醒消息"""
    # 查找该教师关联的用户
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id FROM teacher_basic_info WHERE id = %s
    """, (teacher_id,))

    row = cursor.fetchone()
    if row and row[0]:
        user_id = row[0]
        title = f"待办提醒：{todo_title}"
        content = f"教师 {teacher_name} 您好，您有待办事项需要处理：{todo_title}，截止日期：{due_date}"
        MessageService.create_message(user_id, title, content, "warning", "todo", teacher_id)
        logger.info(f"发送待办提醒: 教师={teacher_name}, 待办={todo_title}")

    cursor.close()
    conn.close()


def send_overdue_alert(teacher_id: int, teacher_name: str, todo_title: str):
    """发送逾期警告消息"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id FROM teacher_basic_info WHERE id = %s
    """, (teacher_id,))

    row = cursor.fetchone()
    if row and row[0]:
        user_id = row[0]
        title = f"⚠️ 逾期警告：{todo_title}"
        content = f"教师 {teacher_name} 您好，您有逾期未完成的待办事项：{todo_title}，请尽快处理！"
        MessageService.create_message(user_id, title, content, "error", "todo", teacher_id)
        logger.warning(f"发送逾期警告: 教师={teacher_name}, 待办={todo_title}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    # 测试
    print("消息服务测试")
    # count = MessageService.get_unread_count(1)
    # print(f"未读消息: {count} 条")
