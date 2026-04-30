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

# 查询所有旧的到龄退休提醒（内部表类型）
print('更新旧的到龄退休提醒为新的格式...')
cursor.execute('''
    SELECT id, 教师ID, 教师姓名, 任务项列表
    FROM todo_work
    WHERE 清单名称 LIKE '%到龄退休提醒%'
    AND 状态 IN ('pending', '待处理', '进行中')
''')

rows = cursor.fetchall()
updated_count = 0

for row in rows:
    todo_id = row[0]
    teacher_id = row[1]
    teacher_name = row[2]
    task_items_raw = row[3]

    try:
        if isinstance(task_items_raw, str):
            task_items = json.loads(task_items_raw)
        elif isinstance(task_items_raw, list):
            task_items = task_items_raw
        else:
            continue

        if not task_items:
            continue

        task = task_items[0]
        task_type = task.get('类型', '')

        # 只更新内部表类型的任务
        if task_type == '内部表':
            # 获取原来的说明文字
            old_desc = task.get('说明', f'教师{teacher_name}需要办理退休手续')

            # 构建新的任务项（退休处理类型，两个选项）
            new_task_items = [{
                "标题": f"请为{teacher_name}办理退休手续",
                "说明": old_desc,
                "类型": "退休处理",
                "目标": "retirement_processing",
                "参数": {
                    "教师ID": teacher_id,
                    "教师姓名": teacher_name,
                    "选项": [
                        {
                            "label": "modify_status",
                            "名称": "修改任职状态",
                            "说明": "请在教师基础信息表中修改当前教师的任职状态",
                            "目标表": "teacher_basic_info",
                            "操作": "修改任职状态"
                        },
                        {
                            "label": "delayed_retirement",
                            "名称": "已批准延迟退休",
                            "说明": "该教师已批准延迟退休，请核实延迟退休记录",
                            "目标表": "delayed_retirement_records",
                            "操作": "核实/填写延迟退休记录"
                        }
                    ]
                },
                "完成状态": task.get('完成状态', False),
                "已选选项": None
            }]

            # 更新数据库
            cursor.execute('''
                UPDATE todo_work
                SET 任务项列表 = %s
                WHERE id = %s
            ''', (json.dumps(new_task_items), todo_id))

            updated_count += 1
            print(f'  已更新 ID={todo_id}, 教师={teacher_name}')

    except Exception as e:
        print(f'  更新失败 ID={todo_id}: {e}')

conn.commit()
print(f'\n共更新 {updated_count} 条记录')

cursor.close()
conn.close()
