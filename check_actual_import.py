#!/usr/bin/env python3
"""
检查数据库中实际导入的数据量
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # 1. 检查 teacher_record 表的数据量
    cursor.execute("SELECT COUNT(*) FROM teacher_record")
    count = cursor.fetchone()[0]
    print(f"teacher_record 表当前数据量: {count} 条")
    
    # 2. 检查所有数据
    cursor.execute("SELECT id, teacher_id, 姓名, 身份证号码 FROM teacher_record ORDER BY id")
    rows = cursor.fetchall()
    
    print(f"\n所有数据:")
    print("-" * 80)
    for row in rows:
        print(f"  ID: {row[0]}, teacher_id: {row[1]}, 姓名: {row[2]}, 身份证: {row[3]}")
    
    # 3. 统计不同身份证的数量
    cursor.execute("SELECT COUNT(DISTINCT 身份证号码) FROM teacher_record")
    distinct_count = cursor.fetchone()[0]
    print(f"\n不同身份证的数量: {distinct_count}")
    
    # 4. 统计每个身份证出现的次数
    cursor.execute("""
        SELECT 身份证号码, COUNT(*) as cnt
        FROM teacher_record
        GROUP BY 身份证号码
        ORDER BY cnt DESC
        LIMIT 10
    """)
    print(f"\n身份证出现次数统计（前10）:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} 次")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check()
