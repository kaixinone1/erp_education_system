"""
检查系统菜单配置
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

# 查询模块管理表
cursor.execute("""
    SELECT module_id, module_name, table_name, is_enable
    FROM sys_modules 
    ORDER BY display_order
""")

print("系统模块:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} (表: {row[2]}, 启用: {row[3]})")

# 查询是否有模块路由表
cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_name LIKE '%module%' OR table_name LIKE '%menu%'
""")

print("\n模块/菜单相关表:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

cursor.close()
conn.close()
