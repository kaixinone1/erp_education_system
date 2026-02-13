#!/usr/bin/env python3
"""
测试真实场景：使用用户的实际字典表结构
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

print("=" * 80)
print("测试真实场景")
print("=" * 80)

conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

# 1. 查看 dict_data_dictionary 的真实结构
print("\n1. dict_data_dictionary 真实结构:")
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'dict_data_dictionary'
    ORDER BY ordinal_position
""")
columns = cursor.fetchall()
for col in columns:
    print(f"   {col[0]}: {col[1]}")

# 2. 查看真实数据
print("\n2. dict_data_dictionary 真实数据:")
cursor.execute("SELECT * FROM dict_data_dictionary")
col_names = [desc[0] for desc in cursor.description]
print(f"   字段: {col_names}")
for row in cursor.fetchall():
    print(f"   {dict(zip(col_names, row))}")

# 3. 模拟导入过程
print("\n3. 模拟导入过程:")
print("   假设Excel数据:")
print("     姓名: 张三, 身份证号码: 123456, 人才类型: 1")
print("     姓名: 李四, 身份证号码: 789012, 人才类型: 2")

print("\n   值映射配置:")
print("     1 -> 专业技术人才")
print("     2 -> 技术人才")

print("\n   关联过程:")
excel_value = "1"
mapped_value = "专业技术人才"
print(f"     Excel值: {excel_value}")
print(f"     映射后: {mapped_value}")

# 在字典表中查找
cursor.execute("SELECT code, \"人才类型\" FROM dict_data_dictionary WHERE code = %s", (mapped_value,))
result = cursor.fetchone()

if result:
    print(f"     找到字典项: code={result[0]}, 人才类型={result[1]}")
    print(f"     子表应存储: talent_type_name='{result[1]}', talent_type_code='{result[0]}'")
else:
    print(f"     未找到！")

# 4. 确定子表结构
print("\n4. 子表结构应该是:")
print("   - id (主键)")
print("   - teacher_id (关联teacher_basic)")
print("   - name (姓名)")
print("   - id_card (身份证号码)")
print("   - talent_type_code (人才类型code)")
print("   - talent_type_name (人才类型中文名)")
print("   - created_at, updated_at")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("结论:")
print("=" * 80)
print("1. 字典表 dict_data_dictionary 结构: code, 人才类型")
print("2. 没有 id 字段，不能用 id 关联")
print("3. 应该用 code 字段关联，存储 code 和 人才类型 两个值")
