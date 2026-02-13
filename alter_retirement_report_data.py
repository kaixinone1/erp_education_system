#!/usr/bin/env python3
"""修改退休呈报表数据表，添加teacher_id字段"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def alter_table():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 检查teacher_id字段是否存在
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'retirement_report_data' AND column_name = 'teacher_id'
    """)
    
    if not cursor.fetchone():
        # 添加teacher_id字段
        cursor.execute("""
            ALTER TABLE retirement_report_data 
            ADD COLUMN teacher_id INTEGER,
            ADD COLUMN template_id INTEGER
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_retirement_report_teacher_id 
            ON retirement_report_data(teacher_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_retirement_report_template_id 
            ON retirement_report_data(template_id)
        """)
        
        conn.commit()
        print("退休呈报表数据表修改成功！添加了teacher_id和template_id字段")
    else:
        print("teacher_id字段已存在，无需修改")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    alter_table()
