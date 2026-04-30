"""
检查并初始化备注信息统计表
"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def check_table_exists(cursor, table_name):
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = %s
        )
    """, (table_name,))
    return cursor.fetchone()[0]

def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_pay_remarks (
            id SERIAL PRIMARY KEY,
            report_period VARCHAR(20) NOT NULL,
            remark_type VARCHAR(50) NOT NULL,
            teacher_id INTEGER,
            teacher_name VARCHAR(100),
            original_status VARCHAR(50),
            new_status VARCHAR(50),
            original_post VARCHAR(100),
            new_post VARCHAR(100),
            change_category VARCHAR(50),
            change_detail TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("表 performance_pay_remarks 创建成功")

def main():
    conn = get_db_connection()
    cursor = conn.cursor()

    table_name = 'performance_pay_remarks'
    if check_table_exists(cursor, table_name):
        print(f"表 {table_name} 已存在")
    else:
        create_table(cursor)
        conn.commit()
        print(f"表 {table_name} 初始化完成")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
