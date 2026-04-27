"""
触发条件监听服务
定时检测教师信息变化，生成待确认触发事件
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
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


class TriggerMonitor:
    """触发条件监听器"""

    def __init__(self):
        self.last_check_time: Optional[datetime] = None
        self.teacher_status_cache: Dict[str, str] = {}

    def load_teacher_status(self) -> Dict[str, str]:
        """加载当前教师任职状态缓存"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 教师ID, 任职状态
            FROM teacher_basic_info
            WHERE 任职状态 IS NOT NULL
        """)

        status_map = {}
        for row in cursor.fetchall():
            teacher_id = str(row[0])
            status = row[1]
            if teacher_id and status:
                status_map[teacher_id] = status

        cursor.close()
        conn.close()

        return status_map

    def get_trigger_conditions(self) -> List[Dict[str, Any]]:
        """获取所有启用的触发条件"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, condition_name, listen_table, listen_field,
                   trigger_type, trigger_value, template_code, is_enabled
            FROM trigger_conditions
            WHERE is_enabled = true
        """)

        conditions = []
        for row in cursor.fetchall():
            conditions.append({
                "id": row[0],
                "condition_name": row[1],
                "listen_table": row[2],
                "listen_field": row[3],
                "trigger_type": row[4],
                "trigger_value": row[5],
                "template_code": row[6],
                "is_enabled": row[7]
            })

        cursor.close()
        conn.close()

        return conditions

    def check_and_create_triggers(self):
        """检测并创建触发事件"""
        logger.info("开始检测触发条件...")

        # 获取当前教师状态
        current_status = self.load_teacher_status()

        # 如果有缓存，比较变化
        if self.teacher_status_cache:
            self._process_status_changes(current_status)

        # 更新缓存
        self.teacher_status_cache = current_status
        logger.info(f"检测完成，当前教师数: {len(current_status)}")

    def _process_status_changes(self, current_status: Dict[str, str]):
        """处理状态变化"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取触发条件
        conditions = self.get_trigger_conditions()

        # 检查每个教师的状态变化
        for teacher_id, new_status in current_status.items():
            old_status = self.teacher_status_cache.get(teacher_id)

            if old_status and old_status != new_status:
                # 状态发生变化，检查是否匹配触发条件
                for condition in conditions:
                    if (condition["listen_field"] == "employment_status" and
                        condition["trigger_value"] == new_status):

                        # 检查是否已存在待处理的触发事件
                        cursor.execute("""
                            SELECT id FROM pending_triggers
                            WHERE teacher_id = %s
                              AND trigger_reason LIKE %s
                              AND status = 'pending'
                        """, (teacher_id, f"%{new_status}%"))

                        if not cursor.fetchone():
                            # 获取教师姓名
                            cursor.execute("""
                                SELECT 姓名 FROM teacher_basic_info
                                WHERE 教师ID = %s
                            """, (teacher_id,))
                            row = cursor.fetchone()
                            teacher_name = row[0] if row else "未知"

                            # 创建触发事件
                            trigger_reason = f'教师 {teacher_name} 的任职状态从 "{old_status}" 变为 "{new_status}" 状态'

                            cursor.execute("""
                                INSERT INTO pending_triggers (
                                    template_code, teacher_id, teacher_name,
                                    trigger_reason, status, created_at
                                ) VALUES (%s, %s, %s, %s, %s, %s)
                            """, (
                                condition["template_code"],
                                teacher_id,
                                teacher_name,
                                trigger_reason,
                                "pending",
                                datetime.now()
                            ))

                            logger.info(f"创建触发事件: {trigger_reason}")

        conn.commit()
        cursor.close()
        conn.close()

    def run_once(self):
        """运行一次检测"""
        self.check_and_create_triggers()


def run_trigger_monitor():
    """触发监听器运行函数"""
    monitor = TriggerMonitor()
    monitor.run_once()


if __name__ == "__main__":
    print("启动触发条件监听器...")
    run_trigger_monitor()
    print("触发条件监听完成")
