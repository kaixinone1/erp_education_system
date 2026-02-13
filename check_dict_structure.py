#!/usr/bin/env python3
"""
检查字典表结构和数据，确认关联逻辑
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
    print("=" * 80)
    print("检查字典表结构和数据")
    print("=" * 80)
    
    # 1. 检查 dict_talent_type 结构
    print("\n1. dict_talent_type 表结构:")
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'dict_talent_type'
        ORDER BY ordinal_position
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")
    
    # 2. 检查 dict_talent_type 数据
    print("\n2. dict_talent_type 数据:")
    cursor.execute("SELECT * FROM dict_talent_type")
    columns = [desc[0] for desc in cursor.description]
    print(f"   字段: {columns}")
    for row in cursor.fetchall():
        print(f"   {row}")
    
    # 3. 模拟导入数据时的查找逻辑
    print("\n3. 模拟关联查找:")
    
    # 假设Excel中的值是 "1"
    excel_value = "1"
    
    # 值映射
    value_mapping = {'1': '高层次人才', '2': '普通人才'}
    
    # 应用值映射
    mapped_value = value_mapping.get(excel_value, excel_value)
    print(f"   Excel值: {excel_value}")
    print(f"   映射后: {mapped_value}")
    
    # 在字典表中查找
    cursor.execute("SELECT id, code, name FROM dict_talent_type WHERE code = %s", (mapped_value,))
    result = cursor.fetchone()
    
    if result:
        print(f"   查找结果: id={result[0]}, code={result[1]}, name={result[2]}")
        print("   ✅ 关联成功！")
    else:
        print(f"   ❌ 关联失败！字典表中没有 code='{mapped_value}' 的记录")
        
        # 检查所有code值
        cursor.execute("SELECT code FROM dict_talent_type")
        codes = [row[0] for row in cursor.fetchall()]
        print(f"   字典表中所有code: {codes}")
    
    # 4. 如果不使用值映射，直接查找
    print("\n4. 如果不使用值映射，直接查找:")
    cursor.execute("SELECT id, code, name FROM dict_talent_type WHERE code = %s", (excel_value,))
    result = cursor.fetchone()
    
    if result:
        print(f"   查找结果: id={result[0]}, code={result[1]}, name={result[2]}")
    else:
        print(f"   ❌ 失败！字典表中没有 code='{excel_value}' 的记录")
    
finally:
    cursor.close()
    conn.close()
