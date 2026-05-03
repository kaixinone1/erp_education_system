import psycopg2
import json

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)

cursor = conn.cursor()

# 查询李恩源在 todo_items 表中的记录
cursor.execute("""
    SELECT id, teacher_name, title, status, task_items, created_at, completed_at
    FROM todo_items 
    WHERE teacher_name = '李恩源'
    ORDER BY created_at DESC
""")

rows = cursor.fetchall()

print("李恩源在 todo_items 表中的记录：")
print("=" * 80)

for row in rows:
    id, teacher_name, title, status, task_items, created_at, completed_at = row
    
    print(f"\nID: {id}")
    print(f"教师姓名: {teacher_name}")
    print(f"标题: {title}")
    print(f"状态: {status}")
    print(f"创建时间: {created_at}")
    print(f"完成时间: {completed_at}")
    
    # 解析任务项列表
    if task_items:
        if isinstance(task_items, str):
            task_items = json.loads(task_items)
        
        total_tasks = len(task_items) if task_items else 0
        completed_tasks = sum(1 for t in task_items if t.get('completed') or t.get('完成状态')) if task_items else 0
        
        print(f"总任务数: {total_tasks}")
        print(f"已完成数: {completed_tasks}")
        print(f"完成进度: {completed_tasks}/{total_tasks} ({(completed_tasks/total_tasks*100) if total_tasks > 0 else 0:.0f}%)")
        
        print(f"\n任务项详情：")
        for i, task in enumerate(task_items):
            task_name = task.get('title', task.get('标题', task.get('name', f'任务{i+1}')))
            completed = task.get('completed', task.get('完成状态', False))
            print(f"  {i+1}. {task_name} - {'已完成' if completed else '未完成'}")
    
    print("-" * 80)

# 查询 todo_items 表的状态分布
print("\n\ntodo_items 表状态分布：")
cursor.execute("""
    SELECT status, COUNT(*) 
    FROM todo_items 
    GROUP BY status
""")
results = cursor.fetchall()
for status, count in results:
    print(f"  {status}: {count} 条")

cursor.close()
conn.close()
