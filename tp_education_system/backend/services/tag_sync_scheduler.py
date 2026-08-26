"""
标签同步定时任务模块
- 每月1日：检查调出教师，生成标签清理提示
- 每年1月1日：自动清理调离/退休教师到期标签
"""
import logging
import psycopg2
from datetime import datetime, date

logger = logging.getLogger(__name__)

DATABASE_CONFIG = {
    "host": "localhost", "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user", "password": "taiping_password"
}

# 调离时保留至次年自然年的标签ID
TRANSFER_AWAY_KEEP_TAGS = {6, 7, 8}  # 年度考核, 人事年报, 工资年报


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def check_transfer_out_reminders():
    """
    每月1日执行：检查调出教师，生成标签清理提醒
    调出教师每月1日提示："[姓名]老师于YYYY年MM月DD日调出（去向），是否修改标签关系？"
    """
    today = date.today()
    if today.day != 1:
        logger.info(f"[标签同步] 今天不是1日({today.day}日)，跳过调出提醒检查")
        return

    logger.info(f"[标签同步] 开始检查调出教师标签清理提醒...")
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 查询所有调出状态的教师
        cur.execute("""
            SELECT id, "姓名", "调出日期", "调出去向"
            FROM teacher_basic_info
            WHERE "任职状态" = '调出'
              AND "调出日期" IS NOT NULL
        """)
        transfer_out_teachers = cur.fetchall()

        if not transfer_out_teachers:
            logger.info("[标签同步] 没有调出教师需要提醒")
            cur.close()
            return

        reminders = []
        for teacher in transfer_out_teachers:
            teacher_id = teacher[0]
            teacher_name = teacher[1]
            transfer_date = teacher[2]
            transfer_direction = teacher[3] or '未知'

            # 格式化日期
            if isinstance(transfer_date, date):
                date_str = f"{transfer_date.year}年{transfer_date.month}月{transfer_date.day}日"
            else:
                date_str = str(transfer_date)

            reminder_msg = (
                f"{teacher_name}老师于{date_str}调出（{transfer_direction}），"
                f"是否修改标签关系？"
            )

            # 检查是否已有该提醒（避免重复创建）
            cur.execute("""
                SELECT id FROM todo_items
                WHERE teacher_id = %s
                  AND title LIKE %s
                  AND status = 'pending'
            """, (teacher_id, f"%调出%标签%"))

            if not cur.fetchone():
                # 创建提醒待办
                cur.execute("""
                    INSERT INTO todo_items
                    (teacher_id, template_id, business_type, teacher_name, title, description, task_items, status, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    teacher_id,
                    'tag_cleanup_transfer_out',
                    'TAG_CLEANUP',
                    teacher_name,
                    f"调出标签清理：{teacher_name}",
                    reminder_msg,
                    '[{"任务名称": "审查标签关系", "描述": "' + reminder_msg + '"}]',
                    "pending",
                    "system"
                ))

            reminders.append(reminder_msg)

        conn.commit()
        cur.close()
        logger.info(f"[标签同步] 调出提醒完成，共{len(reminders)}个提醒：{reminders}")

    except Exception as e:
        logger.error(f"[标签同步] 调出提醒检查失败: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
    finally:
        if conn:
            conn.close()


def cleanup_expired_tags():
    """
    每年1月1日执行：自动清理调离/退休教师到期标签
    - 调离教师：清理年度考核(6)、人事年报(7)、工资年报(8)（保留至次年自然年）
    - 退休教师：清理年度考核(6)、人事年报(7)、工资年报(8)（保留至次年自然年）
    """
    today = date.today()
    if today.month != 1 or today.day != 1:
        logger.info(f"[标签同步] 今天不是1月1日({today.month}月{today.day}日)，跳过到期标签清理")
        return

    logger.info(f"[标签同步] 开始清理到期标签...")
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        current_year = today.year

        # 1. 清理调离教师的到期标签（调离日期在上一年及之前）
        cur.execute("""
            SELECT id, "姓名", "调离日期"
            FROM teacher_basic_info
            WHERE "任职状态" = '调离'
              AND "调离日期" IS NOT NULL
        """)
        transfer_away_teachers = cur.fetchall()

        cleaned_count = 0
        for teacher in transfer_away_teachers:
            teacher_id = teacher[0]
            teacher_name = teacher[1]
            transfer_away_date = teacher[2]

            # 检查调离日期是否在上一年及之前
            if isinstance(transfer_away_date, date):
                if transfer_away_date.year >= current_year:
                    continue  # 今年调离的，保留到明年

            # 清理到期标签
            for tag_id in TRANSFER_AWAY_KEEP_TAGS:
                cur.execute("""
                    DELETE FROM employee_tag_relations
                    WHERE employee_id = %s AND tag_id = %s
                """, (teacher_id, tag_id))
                if cur.rowcount > 0:
                    cleaned_count += 1
                    logger.info(f"[标签同步] 清理调离教师{teacher_name}标签ID={tag_id}")

        # 2. 清理退休教师的到期标签（退休日期在上一年及之前）
        cur.execute("""
            SELECT id, "姓名", "退休日期"
            FROM teacher_basic_info
            WHERE "任职状态" = '退休'
              AND "退休日期" IS NOT NULL
        """)
        retired_teachers = cur.fetchall()

        for teacher in retired_teachers:
            teacher_id = teacher[0]
            teacher_name = teacher[1]
            retirement_date = teacher[2]

            # 检查退休日期是否在上一年及之前
            if isinstance(retirement_date, date):
                if retirement_date.year >= current_year:
                    continue  # 今年退休的，保留到明年

            # 清理到期标签
            for tag_id in TRANSFER_AWAY_KEEP_TAGS:
                cur.execute("""
                    DELETE FROM employee_tag_relations
                    WHERE employee_id = %s AND tag_id = %s
                """, (teacher_id, tag_id))
                if cur.rowcount > 0:
                    cleaned_count += 1
                    logger.info(f"[标签同步] 清理退休教师{teacher_name}标签ID={tag_id}")

        conn.commit()
        cur.close()
        logger.info(f"[标签同步] 到期标签清理完成，共清理{cleaned_count}个标签")

    except Exception as e:
        logger.error(f"[标签同步] 到期标签清理失败: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
    finally:
        if conn:
            conn.close()