import psycopg2
import json

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 添加退休到龄提醒
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
    INSERT INTO business_checklist ("清单名称", "触发条件", "是否有效", "关联模板ID", "任务项列表", created_at, updated_at)
    VALUES ('退休到龄提醒', '["自动扫描"]', true, 4, %s, NOW(), NOW())
''', (json.dumps(retire_remind_tasks),))

conn.commit()

# 验证
cur.execute('SELECT id, "清单名称", "任务项列表" FROM business_checklist ORDER BY id')
print('=== business_checklist ===')
for row in cur.fetchall():
    tasks = row[2]
    if tasks:
        if isinstance(tasks, str):
            tasks = json.loads(tasks)
        print(f'ID:{row[0]} {row[1]} - {len(tasks)}项')

conn.close()
print('\n完成!')
