#!/usr/bin/env python3
"""
调试API查询
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

try:
    # 检查表中的字段
    print("1. 检查 teacher_log 表字段:")
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'teacher_log'
        ORDER BY ordinal_position
    """)
    columns = [row[0] for row in cursor.fetchall()]
    print(f"   字段: {columns}")
    
    # 检查 dict_position 表
    print("\n2. 检查 dict_position 表:")
    cursor.execute("SELECT id, code, name FROM dict_position")
    for row in cursor.fetchall():
        print(f"   {row}")
    
    # 测试简单查询
    print("\n3. 测试简单查询:")
    cursor.execute("SELECT COUNT(*) FROM teacher_log")
    count = cursor.fetchone()[0]
    print(f"   总条数: {count}")
    
    # 测试带JOIN的查询
    print("\n4. 测试带JOIN的查询:")
    try:
        cursor.execute("""
            SELECT t.name, t.id_card, t.position_level, 
                   dict_position.name as position_level_名称
            FROM teacher_log t
            LEFT JOIN dict_position ON CAST(t.position_level AS TEXT) = CAST(dict_position.code AS TEXT)
            LIMIT 5
        """)
        rows = cursor.fetchall()
        print(f"   返回 {len(rows)} 条:")
        for row in rows:
            print(f"   {row}")
    except Exception as e:
        print(f"   查询失败: {e}")
    
    # 检查 position_level 字段的值
    print("\n5. 检查 position_level 字段的值:")
    cursor.execute("SELECT DISTINCT position_level FROM teacher_log LIMIT 10")
    values = [row[0] for row in cursor.fetchall()]
    print(f"   值: {values}")
    
    # 检查 dict_position.code 的值
    print("\n6. 检查 dict_position.code 的值:")
    cursor.execute("SELECT code FROM dict_position")
    codes = [row[0] for row in cursor.fetchall()]
    print(f"   值: {codes}")
    
finally:
    cursor.close()
    conn.close()
