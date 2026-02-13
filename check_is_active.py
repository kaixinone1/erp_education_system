#!/usr/bin/env python3
"""检查是否有效字段"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def check():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 查询是否有效字段的值
    cursor.execute("""
        SELECT id, 清单名称, 是否有效, pg_typeof(是否有效)
        FROM business_checklist
    """)
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"名称: {row[1]}")
        print(f"是否有效: {row[2]} (类型: {row[3]})")
        print(f"是否有效 == True: {row[2] == True}")
        print()
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check()
