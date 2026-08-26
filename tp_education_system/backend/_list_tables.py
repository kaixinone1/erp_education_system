"""
临时数据库检查脚本 - 先列出所有表名
"""
import psycopg2

conn_info = {
    "host": "localhost",
    "port": 5432,
    "database": "taiping_education_fifteen",
    "user": "taiping_user",
    "password": "taiping_password"
}

conn = psycopg2.connect(**conn_info)
cur = conn.cursor()

# 先列出所有表
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
""")
tables = cur.fetchall()
print("数据库中所有表:")
for t in tables:
    print(f"  {t[0]}")

# 搜索包含 title 的表
title_tables = [t[0] for t in tables if 'title' in t[0].lower()]
print(f"\n包含 'title' 的表: {title_tables}")

# 搜索包含 post 的表
post_tables = [t[0] for t in tables if 'post' in t[0].lower() or 'appointment' in t[0].lower()]
print(f"包含 'post'/'appointment' 的表: {post_tables}")

# 搜索包含 teacher 的表
teacher_tables = [t[0] for t in tables if 'teacher' in t[0].lower()]
print(f"包含 'teacher' 的表: {teacher_tables}")

cur.close()
conn.close()