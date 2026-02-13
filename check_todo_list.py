#!/usr/bin/env python3
"""检查待办工作列表数据"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def check():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 查看待办工作表
    print("=== 待办工作表 (todo_work) ===")
    cursor.execute("SELECT id, teacher_id, teacher_name, checklist_name, status FROM todo_work ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    print(f"记录数: {len(rows)}")
    for row in rows:
        print(f"  ID:{row[0]}, 教师:{row[2]}, 清单:{row[3]}, 状态:{row[4]}")
    
    # 查看任务项表
    print("\n=== 任务项表 (todo_task_items) ===")
    cursor.execute("SELECT id, todo_id, 序号, 标题, 类型, 完成状态 FROM todo_task_items ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    print(f"记录数: {len(rows)}")
    for row in rows:
        print(f"  ID:{row[0]}, 待办ID:{row[1]}, 序号:{row[2]}, 标题:{row[3]}, 类型:{row[4]}, 完成:{row[5]}")
    
    # 检查是否有待办工作
    cursor.execute("SELECT COUNT(*) FROM todo_work WHERE status = 'pending'")
    count = cursor.fetchone()[0]
    print(f"\n待处理的工作数量: {count}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check()
