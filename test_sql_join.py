#!/usr/bin/env python3
"""测试 SQL JOIN"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 测试 JOIN
sql = """
SELECT 
    t.education_type,
    dict_education_type.education_type as education_type_name
FROM teacher_education_record t
LEFT JOIN dict_education_type_dictionary dict_education_type
    ON CAST(t.education_type AS TEXT) = CAST(dict_education_type.education_type AS TEXT)
LIMIT 5
"""

print("测试 JOIN 查询:")
cursor.execute(sql)
for row in cursor.fetchall():
    print(f"  education_type={row[0]}, education_type_name={row[1]}")

# 检查数据类型
print("\n检查 education_type 字段的数据类型:")
cursor.execute("""
    SELECT data_type 
    FROM information_schema.columns 
    WHERE table_name = 'teacher_education_record' AND column_name = 'education_type'
""")
print(f"  teacher_education_record.education_type: {cursor.fetchone()[0]}")

cursor.execute("""
    SELECT data_type 
    FROM information_schema.columns 
    WHERE table_name = 'dict_education_type_dictionary' AND column_name = 'education_type'
""")
print(f"  dict_education_type_dictionary.education_type: {cursor.fetchone()[0]}")

# 直接比较
print("\n直接比较值:")
cursor.execute("SELECT education_type FROM teacher_education_record LIMIT 1")
teacher_val = cursor.fetchone()[0]
print(f"  教师表值: '{teacher_val}' (类型: {type(teacher_val)})")

cursor.execute("SELECT education_type FROM dict_education_type_dictionary LIMIT 1")
dict_val = cursor.fetchone()[0]
print(f"  字典表值: '{dict_val}' (类型: {type(dict_val)})")

cursor.close()
conn.close()
