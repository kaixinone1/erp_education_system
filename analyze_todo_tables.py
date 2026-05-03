import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)

cursor = conn.cursor()

print("=" * 80)
print("待办系统表结构分析")
print("=" * 80)

# 1. 检查 todo_work 表
print("\n1. todo_work 表：")
cursor.execute("""
    SELECT COUNT(*) FROM todo_work
""")
todo_work_count = cursor.fetchone()[0]
print(f"   总记录数: {todo_work_count}")

cursor.execute("""
    SELECT 状态, COUNT(*) FROM todo_work GROUP BY 状态
""")
print("   状态分布:")
for status, count in cursor.fetchall():
    print(f"     - {status}: {count} 条")

cursor.execute("""
    SELECT MIN(created_at), MAX(created_at) FROM todo_work
""")
min_time, max_time = cursor.fetchone()
print(f"   创建时间范围: {min_time} 至 {max_time}")

# 2. 检查 todo_items 表
print("\n2. todo_items 表：")
cursor.execute("""
    SELECT COUNT(*) FROM todo_items
""")
todo_items_count = cursor.fetchone()[0]
print(f"   总记录数: {todo_items_count}")

cursor.execute("""
    SELECT status, COUNT(*) FROM todo_items GROUP BY status
""")
print("   状态分布:")
for status, count in cursor.fetchall():
    print(f"     - {status}: {count} 条")

cursor.execute("""
    SELECT MIN(created_at), MAX(created_at) FROM todo_items
""")
min_time, max_time = cursor.fetchone()
print(f"   创建时间范围: {min_time} 至 {max_time}")

# 3. 检查表结构差异
print("\n3. 表结构对比：")

cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'todo_work'
    ORDER BY ordinal_position
""")
todo_work_columns = cursor.fetchall()
print(f"   todo_work 表字段 ({len(todo_work_columns)} 个):")
for col_name, col_type in todo_work_columns:
    print(f"     - {col_name} ({col_type})")

cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'todo_items'
    ORDER BY ordinal_position
""")
todo_items_columns = cursor.fetchall()
print(f"\n   todo_items 表字段 ({len(todo_items_columns)} 个):")
for col_name, col_type in todo_items_columns:
    print(f"     - {col_name} ({col_type})")

# 4. 检查数据重叠
print("\n4. 数据重叠检查：")
cursor.execute("""
    SELECT DISTINCT 清单名称 FROM todo_work
""")
todo_work_names = [row[0] for row in cursor.fetchall()]
print(f"   todo_work 清单名称: {todo_work_names}")

cursor.execute("""
    SELECT DISTINCT title FROM todo_items
""")
todo_items_titles = [row[0] for row in cursor.fetchall()]
print(f"   todo_items 标题: {todo_items_titles[:10]}...")  # 只显示前10个

cursor.close()
conn.close()
