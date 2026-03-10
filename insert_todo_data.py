import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 清空现有数据
cursor.execute("DELETE FROM todo_work_items")

# 插入示例待办工作
todo_items = [
    ('待审核的职工退休申请', '有3条职工退休申请需要审核', 'retirement', 293, 'pending', 'high'),
    ('待处理的职务升降申报', '有2条职务升降申报需要处理', 'promotion', 293, 'pending', 'normal'),
    ('待确认的信息变更', '有5条教师信息变更需要确认', 'info_change', 293, 'pending', 'normal'),
    ('待导出的报表', '月度统计报表需要导出', 'report', None, 'pending', 'low'),
]

for item in todo_items:
    cursor.execute("""
        INSERT INTO todo_work_items (title, description, module_id, teacher_id, status, priority)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, item)

conn.commit()
cursor.close()
conn.close()

print(f"已插入 {len(todo_items)} 条待办工作数据")
