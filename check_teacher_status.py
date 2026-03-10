"""
检查教师基础信息表结构和任职状态字段
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查询教师基础信息表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'teacher_basic_info'
    ORDER BY ordinal_position
""")

print("teacher_basic_info 表结构:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# 检查 employment_status 字段的值
print("\nemployment_status (任职状态) 字段的值分布:")
cursor.execute("""
    SELECT employment_status, COUNT(*) 
    FROM teacher_basic_info 
    GROUP BY employment_status
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}条")

cursor.close()
conn.close()
