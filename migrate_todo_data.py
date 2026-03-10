"""
迁移待办工作数据
从原来的表（如果有）迁移到我创建的 todo_work_items 表
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

# 检查是否存在原来的 todo_work 表（中文字段名）
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'todo_work'
""")

old_table_exists = cursor.fetchone()

if old_table_exists:
    print("发现原来的 todo_work 表，开始迁移数据...")
    
    # 获取原表数据
    try:
        cursor.execute("""
            SELECT id, 教师ID, 清单ID, 清单名称, 教师姓名, 
                   任务项列表, 总任务数, 已完成数, 状态, created_at
            FROM todo_work
        """)
        
        rows = cursor.fetchall()
        print(f"原表有 {len(rows)} 条数据")
        
        # 清空新表
        cursor.execute("DELETE FROM todo_work_items")
        
        # 迁移数据
        for row in rows:
            # 构建标题和描述
            title = row[3] if row[3] else "待办工作"  # 清单名称
            description = f"教师: {row[4]}, 任务数: {row[6]}, 已完成: {row[7]}"
            module_id = "retirement"  # 默认模块
            teacher_id = row[1]
            status = row[8] if row[8] else "pending"
            priority = "normal"
            
            cursor.execute("""
                INSERT INTO todo_work_items (title, description, module_id, teacher_id, status, priority)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, description, module_id, teacher_id, status, priority))
        
        conn.commit()
        print(f"成功迁移 {len(rows)} 条数据到 todo_work_items 表")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
else:
    print("未找到原来的 todo_work 表")
    
    # 检查 todo_work_items 表是否有数据
    cursor.execute("SELECT COUNT(*) FROM todo_work_items")
    count = cursor.fetchone()[0]
    print(f"todo_work_items 表现有 {count} 条数据")

cursor.close()
conn.close()
