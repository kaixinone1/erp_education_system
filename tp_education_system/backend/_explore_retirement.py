import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 查找所有包含"退休"的表
print("=== 包含'退休'的表 ===")
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE '%retire%' OR table_name LIKE '%tui%' OR table_name LIKE '%退休%') ORDER BY table_name")
for r in cur.fetchall():
    print(f"  {r[0]}")

# retirement_info 完整数据
print("\n=== retirement_info 所有数据 ===")
cur.execute("SELECT * FROM retirement_info")
cols = [d[0] for d in cur.description]
for row in cur.fetchall():
    d = dict(zip(cols, row))
    print(f"  {d}")

# salary_data - 按身份证号分组查看一个人的所有工资记录
print("\n=== salary_data 一个人所有工资记录 ===")
cur.execute("""
    SELECT id_card_1, type, job_title_post, field_21, time, salary, salary_1
    FROM salary_data WHERE id_card_1 = '341203199612261536'
    ORDER BY time
""")
cols = [d[0] for d in cur.description]
for row in cur.fetchall():
    print(f"  {dict(zip(cols, row))}")

# 检查 salary_data 中起薪时间的范围
print("\n=== salary_data time 范围 ===")
cur.execute("SELECT MIN(time), MAX(time) FROM salary_data WHERE time IS NOT NULL")
r = cur.fetchone()
print(f"  min: {r[0]}, max: {r[1]}")

# 检查 2014-10-01 附近的数据
print("\n=== salary_data 2014-10-01 附近的数据 ===")
cur.execute("SELECT COUNT(*) FROM salary_data WHERE time = '2014-10-01'")
r = cur.fetchone()
print(f"  time='2014-10-01': {r[0]} 条")

# post_appointment_info 的 post_level_1 和 professional_title 不同值
print("\n=== post_appointment_info post_level_1 不同值 ===")
cur.execute("SELECT DISTINCT post_level_1 FROM post_appointment_info WHERE post_level_1 IS NOT NULL LIMIT 30")
for r in cur.fetchall():
    print(f"  {r[0]}")

print("\n=== post_appointment_info professional_title 不同值 ===")
cur.execute("SELECT DISTINCT professional_title FROM post_appointment_info WHERE professional_title IS NOT NULL LIMIT 30")
for r in cur.fetchall():
    print(f"  {r[0]}")

# salary_data 中 job_title_post 不同值
print("\n=== salary_data job_title_post 不同值 ===")
cur.execute("SELECT DISTINCT job_title_post FROM salary_data WHERE job_title_post IS NOT NULL ORDER BY job_title_post")
for r in cur.fetchall():
    print(f"  {r[0]}")

# salary_data 中 type 和 type_1 不同值
print("\n=== salary_data type 不同值 ===")
cur.execute("SELECT DISTINCT type FROM salary_data WHERE type IS NOT NULL")
for r in cur.fetchall():
    print(f"  type: {r[0]}")

print("\n=== salary_data type_1 不同值 ===")
cur.execute("SELECT DISTINCT type_1 FROM salary_data WHERE type_1 IS NOT NULL")
for r in cur.fetchall():
    print(f"  type_1: {r[0]}")

cur.close()
conn.close()