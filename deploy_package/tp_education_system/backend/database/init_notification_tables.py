"""
数据库表初始化脚本
创建消息通知所需的系统表
"""
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def init_system_messages_table():
    """创建系统消息表"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    # 检查表是否存在
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_name = 'system_messages'
    """)
    
    if not cursor.fetchone():
        logger.info("创建 system_messages 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_messages (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                message_type VARCHAR(20) DEFAULT 'info',
                related_type VARCHAR(50),
                related_id INTEGER,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_messages_user_id 
            ON system_messages(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_messages_is_read 
            ON system_messages(is_read)
        """)
        
        conn.commit()
        logger.info("  [OK] system_messages 表创建成功")
    else:
        logger.info("system_messages 表已存在，跳过")

    cursor.close()
    conn.close()


def init_unified_todo_table():
    """创建统一的待办事项表（合并todo_items和todo_work）"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    # 检查表是否存在
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_name = 'unified_todos'
    """)
    
    if not cursor.fetchone():
        logger.info("创建 unified_todos 表...")
        
        # 创建统一的待办表，合并原有两套表的功能
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unified_todos (
                id SERIAL PRIMARY KEY,
                todo_type VARCHAR(20) NOT NULL,  -- 'business' 或 'work'
                template_id VARCHAR(50),         -- 关联模板ID
                business_type VARCHAR(50),       -- 业务类型
                teacher_id INTEGER,              -- 教师ID
                teacher_name VARCHAR(100),       -- 教师姓名
                title VARCHAR(200) NOT NULL,    -- 待办标题
                description TEXT,               -- 描述
                status VARCHAR(20) DEFAULT 'pending',  -- pending/in_progress/completed/returned
                priority VARCHAR(20) DEFAULT 'normal',  -- high/normal/low
                due_date DATE,                 -- 截止日期
                task_items JSONB,              -- 任务项列表
                source VARCHAR(20) DEFAULT 'system',  -- 来源: system/user/auto
                assignee_id INTEGER,           -- 负责人ID
                assignee_name VARCHAR(100),    -- 负责人姓名
                created_by VARCHAR(20) DEFAULT 'system',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                return_reason TEXT
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_unified_todos_type 
            ON unified_todos(todo_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_unified_todos_status 
            ON unified_todos(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_unified_todos_teacher_id 
            ON unified_todos(teacher_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_unified_todos_due_date 
            ON unified_todos(due_date)
        """)
        
        conn.commit()
        logger.info("  [OK] unified_todos 表创建成功")
    else:
        logger.info("unified_todos 表已存在，跳过")

    cursor.close()
    conn.close()


def init_trigger_log_table():
    """创建触发日志表"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_name = 'trigger_logs'
    """)
    
    if not cursor.fetchone():
        logger.info("创建 trigger_logs 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_logs (
                id SERIAL PRIMARY KEY,
                trigger_type VARCHAR(50) NOT NULL,
                teacher_id INTEGER,
                teacher_name VARCHAR(100),
                condition_name VARCHAR(100),
                old_value TEXT,
                new_value TEXT,
                action_taken VARCHAR(20),  -- created/ignored
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trigger_logs_teacher_id 
            ON trigger_logs(teacher_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trigger_logs_created_at 
            ON trigger_logs(created_at)
        """)
        
        conn.commit()
        logger.info("  [OK] trigger_logs 表创建成功")
    else:
        logger.info("trigger_logs 表已存在，跳过")

    cursor.close()
    conn.close()


def init_all_tables():
    """初始化所有表"""
    logger.info("开始初始化数据库表...")
    
    init_system_messages_table()
    init_unified_todo_table()
    init_trigger_log_table()
    
    logger.info("数据库表初始化完成!")


if __name__ == "__main__":
    init_all_tables()
