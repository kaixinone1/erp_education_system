import psycopg2
import json

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 1. 更新退休到龄提醒
retire_remind_tasks = [
    {
        "序号": 1,
        "标题": "请为{教师姓名}办理退休手续",
        "类型": "退休处理",
        "目标": "retirement_processing",
        "参数": {
            "选项": [
                {
                    "label": "modify_status",
                    "名称": "修改任职状态",
                    "操作": "修改任职状态",
                    "说明": "请在教师基础信息表中修改当前教师的任职状态",
                    "目标表": "teacher_basic_info"
                },
                {
                    "label": "delayed_retirement",
                    "名称": "已批准延迟退休",
                    "操作": "核实/填写延迟退休记录",
                    "说明": "该教师已批准延迟退休，请核实延迟退休记录",
                    "目标表": "delayed_retirement_records"
                }
            ],
            "教师ID": None,
            "教师姓名": None
        }
    }
]

cur.execute('''
    UPDATE business_checklist 
    SET "任务项列表" = %s, updated_at = NOW()
    WHERE "清单名称" = '退休到龄提醒'
''', (json.dumps(retire_remind_tasks),))
print('已更新: 退休到龄提醒')

# 2. 更新80周岁高龄补贴提醒
octo_tasks = [
    {"序号": 1, "标题": "收集身份证、户口本复印件", "类型": "收集", "目标": "id_copy", "参数": {"说明": "收集身份证、户口本复印件"}},
    {"序号": 2, "标题": "填写高龄补贴申请表", "类型": "填写", "目标": "apply_form", "参数": {"说明": "填写高龄补贴申请表"}},
    {"序号": 3, "标题": "单位审核盖章", "类型": "审批", "目标": "unit_approve", "参数": {"说明": "单位审核盖章"}},
    {"序号": 4, "标题": "提交民政部门", "类型": "送审", "目标": "civil_affairs", "参数": {"说明": "提交民政部门"}}
]

cur.execute('''
    UPDATE business_checklist 
    SET "任务项列表" = %s, updated_at = NOW()
    WHERE "清单名称" = '80周岁高龄补贴提醒'
''', (json.dumps(octo_tasks),))
print('已更新: 80周岁高龄补贴提醒')

# 3. 更新教师死亡后待办工作
death_tasks = [
    {"序号": 1, "标题": "收集死亡证明", "类型": "收集", "目标": "death_cert", "参数": {"说明": "收集死亡证明"}},
    {"序号": 2, "标题": "打印终保承诺书", "类型": "打印", "目标": "promise_print", "参数": {"说明": "打印终保承诺书"}},
    {"序号": 3, "标题": "扫描上传材料", "类型": "上传", "目标": "upload", "参数": {"说明": "扫描上传材料"}},
    {"序号": 4, "标题": "填报抚恤金审批表", "类型": "填写", "目标": "compensation_form", "参数": {"说明": "填报抚恤金审批表"}},
    {"序号": 5, "标题": "送审材料", "类型": "送审", "目标": "submit", "参数": {"说明": "送审材料"}},
    {"序号": 6, "标题": "机关中心签批", "类型": "审批", "目标": "center_approve", "参数": {"说明": "机关中心签批"}},
    {"序号": 7, "标题": "工资科预审核", "类型": "审批", "目标": "wage_approve", "参数": {"说明": "工资科预审核"}},
    {"序号": 8, "标题": "教育局审批", "类型": "审批", "目标": "education_approve", "参数": {"说明": "教育局审批"}},
    {"序号": 9, "标题": "人社局审批", "类型": "审批", "目标": "hr_approve", "参数": {"说明": "人社局审批"}},
    {"序号": 10, "标题": "财政局备案", "类型": "备案", "目标": "finance_record", "参数": {"说明": "财政局备案"}}
]

cur.execute('''
    UPDATE business_checklist 
    SET "任务项列表" = %s, updated_at = NOW()
    WHERE "清单名称" = '教师死亡后待办工作'
''', (json.dumps(death_tasks),))
print('已更新: 教师死亡后待办工作')

conn.commit()

# 验证
print('\n=== 验证更新结果 ===')
cur.execute('SELECT "清单名称", "任务项列表" FROM business_checklist ORDER BY id')
for row in cur.fetchall():
    tasks = row[1]
    if tasks:
        if isinstance(tasks, str):
            tasks = json.loads(tasks)
        print(f'{row[0]}: {len(tasks)}项')
        for t in tasks:
            print(f'  - {t.get("标题")}')

conn.close()
print('\n完成!')
