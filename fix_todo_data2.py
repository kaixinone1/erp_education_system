import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 获取教师姓名
cursor.execute("SELECT id, name FROM teacher_basic_info WHERE id = 293")
teacher_row = cursor.fetchone()
teacher_name = teacher_row[1] if teacher_row else "未知教师"

print(f"教师姓名: {teacher_name}")

# 更新待办工作数据，添加教师姓名和任务数
todo_updates = [
    (4, '待审核的职工退休申请', teacher_name, 5, 0),
    (5, '待处理的职务升降申报', teacher_name, 3, 0),
    (6, '待确认的信息变更', teacher_name, 5, 0),
    (7, '待导出的报表', teacher_name, 2, 0),
]

for todo_id, title, name, total, completed in todo_updates:
    description = f"教师: {name}, 任务数: {total}, 已完成: {completed}"
    cursor.execute("""
        UPDATE todo_work_items 
        SET title = %s, description = %s
        WHERE id = %s
    """, (title, description, todo_id))

conn.commit()

# 验证更新
cursor.execute("SELECT id, title, description FROM todo_work_items")
rows = cursor.fetchall()
print("\n更新后的数据:")
for row in rows:
    print(f"  ID={row[0]}, 标题={row[1]}, 描述={row[2]}")

cursor.close()
conn.close()

print("\n数据修复完成")
