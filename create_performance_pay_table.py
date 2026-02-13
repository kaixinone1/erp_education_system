#!/usr/bin/env python3
"""创建绩效工资审批表"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def create_table():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 创建绩效工资审批表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_pay_approval (
            id SERIAL PRIMARY KEY,
            教师ID INTEGER UNIQUE,
            教师姓名 VARCHAR(100),
            绩效工资 DECIMAL(10, 2),
            汇总日期 DATE,
            备注 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("绩效工资审批表创建成功！")

if __name__ == '__main__':
    create_table()
