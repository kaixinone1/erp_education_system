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

# 新的任务项结构（包含两个选项）
new_task_items = [
    {
        "标题": "请为王会丽办理退休手续",
        "说明": "教师王会丽（55岁）今年退休，请及时办理退休手续",
        "类型": "退休处理",
        "目标": "retirement_processing",
        "参数": {
            "教师ID": 173,
            "教师姓名": "王会丽",
            "年龄": 55,
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
        "完成状态": False,
        "已选选项": None
    }
]

# 更新王会丽的待办数据
cursor.execute("""
    UPDATE todo_work 
    SET 任务项列表 = %s
    WHERE id = 15
""", (json.dumps(new_task_items, ensure_ascii=False),))

print(f"更新了 {cursor.rowcount} 条记录")

conn.commit()
cursor.close()
conn.close()

print("更新完成！")
