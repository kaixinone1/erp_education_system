#!/usr/bin/env python3
"""检查清单配置"""
import psycopg2
import json

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def check_config():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 查询所有清单配置
    cursor.execute("""
        SELECT id, 清单名称, 触发条件, 是否有效
        FROM business_checklist
    """)
    
    checklists = cursor.fetchall()
    print("业务清单配置:")
    for row in checklists:
        print(f"  ID: {row[0]}")
        print(f"  名称: {row[1]}")
        print(f"  触发条件: {row[2]}")
        print(f"  是否有效: {row[3]}")
        print()
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_config()
