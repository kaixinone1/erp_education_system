#!/usr/bin/env python3
"""调试状态变更"""
import psycopg2
import json

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def debug():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    target_status = "退休"
    
    # 查找所有有效的清单模板
    cursor.execute("""
        SELECT id, 清单名称, 任务项列表, 触发条件
        FROM business_checklist
        WHERE 是否有效 = true
    """)
    
    all_checklists = cursor.fetchall()
    print(f"找到 {len(all_checklists)} 个有效清单")
    
    for checklist_row in all_checklists:
        checklist_id = checklist_row[0]
        checklist_name = checklist_row[1]
        task_items = checklist_row[2] if isinstance(checklist_row[2], list) else json.loads(checklist_row[2]) if checklist_row[2] else []
        trigger_condition = checklist_row[3] if isinstance(checklist_row[3], dict) else json.loads(checklist_row[3]) if checklist_row[3] else {}
        
        print(f"\n清单: {checklist_name}")
        print(f"  触发条件: {trigger_condition}")
        print(f"  触发条件类型: {type(trigger_condition)}")
        
        # 检查触发条件是否匹配当前状态
        target_statuses = trigger_condition.get("target_status", [])
        print(f"  target_statuses: {target_statuses}")
        print(f"  target_statuses类型: {type(target_statuses)}")
        
        if isinstance(target_statuses, str):
            target_statuses = [target_statuses]
        
        # 如果当前状态在触发列表中，创建待办
        if target_status in target_statuses:
            print(f"  ✓ 匹配成功！")
        else:
            print(f"  ✗ 不匹配")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    debug()
