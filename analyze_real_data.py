#!/usr/bin/env python3
"""
分析真实数据结构 - 从基本原理出发
"""

import psycopg2
import pandas as pd

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

print("=" * 80)
print("分析真实数据结构")
print("=" * 80)

# 1. 查看所有字典表
print("\n1. 查看所有字典表（表名包含dict的表）:")
conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    AND table_name LIKE 'dict_%'
    ORDER BY table_name
""")

dict_tables = [row[0] for row in cursor.fetchall()]
for table in dict_tables:
    print(f"   {table}")

# 2. 查看每个字典表的结构和数据
print("\n2. 字典表详细内容:")
for table in dict_tables:
    print(f"\n   【{table}】")
    
    # 获取表结构
    cursor.execute(f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print(f"   结构: {[(c[0], c[1]) for c in columns]}")
    
    # 获取数据
    try:
        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
        data = cursor.fetchall()
        if data:
            col_names = [desc[0] for desc in cursor.description]
            print(f"   数据示例:")
            for row in data:
                print(f"      {dict(zip(col_names, row))}")
    except Exception as e:
        print(f"   读取数据失败: {e}")

# 3. 分析关联原理
print("\n" + "=" * 80)
print("3. 子表-字典表关联原理分析")
print("=" * 80)
print("""
关联的基本原理：

子表字段值 ──→ 值映射（可选）──→ 字典表.code ──→ 字典表.id/name

例如：
Excel中的值: "1" 
    ↓
值映射: "1" → "干部"（如果字典表的code是"干部"而不是"1"）
    ↓
在字典表中查找 code="干部" → 获取 id=1, name="干部"
    ↓
子表存储: talent_type_id=1, talent_type_name="干部", talent_type_code="干部"

关键问题：
1. 您的字典表的 code 字段存储的是什么？（是"1"还是"干部"？）
2. Excel中的原始值是什么？
3. 是否需要值映射？
""")

# 4. 检查是否有现成的人才类型字典
print("\n4. 检查是否存在人才类型相关字典:")
for table in dict_tables:
    if 'talent' in table.lower() or '人才' in table.lower() or 'type' in table.lower():
        print(f"   找到: {table}")
        cursor.execute(f"SELECT * FROM {table}")
        col_names = [desc[0] for desc in cursor.description]
        print(f"   字段: {col_names}")
        for row in cursor.fetchall():
            print(f"      {dict(zip(col_names, row))}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("结论：")
print("=" * 80)
print("请根据上述真实字典表结构，确定：")
print("1. 使用哪个字典表？")
print("2. 字典表的code字段是什么？")
print("3. Excel中的原始值是否需要映射？")
