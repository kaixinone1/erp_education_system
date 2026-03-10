"""
恢复原来的待办工作系统
"""
import psycopg2
import json

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 1. 删除我创建的 todo_work_items 表
cursor.execute("DROP TABLE IF EXISTS todo_work_items CASCADE")
print("已删除 todo_work_items 表")

# 2. 创建原来的 todo_work 表结构（中文字段名）
cursor.execute("""
    CREATE TABLE IF NOT EXISTS todo_work (
        id SERIAL PRIMARY KEY,
        教师ID INTEGER,
        清单ID INTEGER,
        清单名称 VARCHAR(200),
        教师姓名 VARCHAR(100),
        任务项列表 JSONB,
        总任务数 INTEGER DEFAULT 0,
        已完成数 INTEGER DEFAULT 0,
        状态 VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
print("已创建 todo_work 表")

# 3. 从 business_checklist 获取清单模板
cursor.execute("SELECT id, 清单名称, 任务项列表 FROM business_checklist WHERE 是否有效 = true LIMIT 1")
template = cursor.fetchone()

if template:
    checklist_id = template[0]
    checklist_name = template[1]
    task_items = template[2]
    
    print(f"找到清单模板: {checklist_name}")
    
    # 4. 获取教师信息（ID=293）
    cursor.execute("SELECT id, name FROM teacher_basic_info WHERE id = 293")
    teacher = cursor.fetchone()
    
    if teacher:
        teacher_id = teacher[0]
        teacher_name = teacher[1]
        
        # 计算总任务数
        total_tasks = len(task_items) if task_items else 0
        
        # 5. 创建待办工作
        cursor.execute("""
            INSERT INTO todo_work (教师ID, 清单ID, 清单名称, 教师姓名, 任务项列表, 总任务数, 已完成数, 状态)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (teacher_id, checklist_id, checklist_name, teacher_name, json.dumps(task_items), total_tasks, 0, 'pending'))
        
        print(f"已为教师 {teacher_name} 创建待办工作，共 {total_tasks} 个任务")
    else:
        print("未找到教师信息")
else:
    print("未找到有效的清单模板")

conn.commit()

# 6. 验证恢复结果
cursor.execute("SELECT * FROM todo_work")
rows = cursor.fetchall()
print(f"\n恢复完成，todo_work 表共有 {len(rows)} 条数据")
for row in rows:
    print(f"  ID={row[0]}, 教师={row[4]}, 清单={row[3]}, 任务数={row[6]}")

cursor.close()
conn.close()
print("\n待办工作系统恢复完成")
