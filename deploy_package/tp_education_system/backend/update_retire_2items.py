import psycopg2
import json

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 退休到龄提醒 - 2个任务项（单选）
retire_remind_tasks = [
    {
        "序号": 1,
        "标题": "修改任职状态",
        "类型": "退休处理",
        "目标": "modify_status",
        "参数": {
            "说明": "请在教师基础信息表中修改当前教师的任职状态",
            "目标表": "teacher_basic_info"
        }
    },
    {
        "序号": 2,
        "标题": "已批准延迟退休",
        "类型": "退休处理",
        "目标": "delayed_retirement",
        "参数": {
            "说明": "该教师已批准延迟退休，请核实延迟退休记录",
            "目标表": "delayed_retirement_records"
        }
    }
]

cur.execute('''
    UPDATE business_checklist 
    SET "任务项列表" = %s, updated_at = NOW()
    WHERE "清单名称" = '退休到龄提醒'
''', (json.dumps(retire_remind_tasks),))

conn.commit()

# 验证
cur.execute('SELECT "清单名称", "任务项列表" FROM business_checklist WHERE "清单名称" = %s', ('退休到龄提醒',))
row = cur.fetchone()
if row:
    tasks = row[1]
    if isinstance(tasks, str):
        tasks = json.loads(tasks)
    print('=== 退休到龄提醒 ===')
    for t in tasks:
        print(f'{t.get("序号")}. {t.get("标题")} ({t.get("类型")})')

conn.close()
print('\n完成!')
