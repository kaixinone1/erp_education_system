#!/usr/bin/env python3
"""更新退休业务清单为规定的7项任务"""
import psycopg2
import json

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def update_checklist():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 严格按照规定的7项任务
    task_items = [
        {
            "序号": 1,
            "标题": "填报《退休呈报表》",
            "类型": "内部表",
            "目标": "retirement_report_form",
            "参数": {
                "说明": "点击时打开数据管理界面，呈报退休呈报表，点击新增，弹出当前教师姓名，身份证号码信息，确认后，自动填报退休呈报表",
                "预填字段": ["教师姓名", "身份证号码"]
            },
            "完成状态": False
        },
        {
            "序号": 2,
            "标题": "填报《待遇申领表》",
            "类型": "外部链接",
            "目标": "http://zwfw.hubei.gov.cn/webview/fw/frfw.html",
            "参数": {
                "说明": "点击时跳转至湖北政务网登录界面"
            },
            "完成状态": False
        },
        {
            "序号": 3,
            "标题": "填报《职务升级表》",
            "类型": "内部表",
            "目标": "position_upgrade_form",
            "参数": {
                "说明": "点击时打开数据管理界面，呈报职务升降表，点击新增，弹出当前教师姓名，身份证号码信息，确认后，自动填报职务升降表",
                "预填字段": ["教师姓名", "身份证号码"]
            },
            "完成状态": False
        },
        {
            "序号": 4,
            "标题": "绩效工资自动增加退休人员绩效",
            "类型": "自动汇总",
            "目标": "performance_pay_summary",
            "参数": {
                "说明": "根据退休时的职务（高级、一级、二级、三级）增加退休教师姓名：在备注栏下，自动汇总",
                "汇总规则": [
                    "1.高级退休X人：XXX、XXX，把姓名依次粘贴到冒号后面",
                    "2.一级退休X人：XXX、XXX，把姓名依次粘贴到冒号后面",
                    "3.二级退休X人：XXX、XXX，把姓名依次粘贴到冒号后面",
                    "4.三级退休X人：XXX、XXX，把姓名依次粘贴到冒号后面"
                ]
            },
            "完成状态": False
        },
        {
            "序号": 5,
            "标题": "录入《湖北老干部》网",
            "类型": "外部链接",
            "目标": "https://admin.hblgj.gov.cn/IpWHRdyAcT.php/member?ref=addtabs",
            "参数": {
                "说明": "点击跳转至湖北老干部网登录网页"
            },
            "完成状态": False
        },
        {
            "序号": 6,
            "标题": "上传审核材料至湖北政务网",
            "类型": "外部链接",
            "目标": "http://zwfw.hubei.gov.cn/webview/fw/frfw.html",
            "参数": {
                "说明": "上传经教育局、人社局审核通过并加盖公章的《退休待遇申领表》、《退休呈报表》、《职务升级表》至湖北政务网"
            },
            "完成状态": False
        },
        {
            "序号": 7,
            "标题": "发签退休证",
            "类型": "签发证件",
            "目标": "retirement_certificate",
            "参数": {
                "说明": "签收人姓名，签收日期YYYY-MM-DD",
                "字段": ["签收人姓名", "签收日期"]
            },
            "完成状态": False
        }
    ]
    
    cursor.execute("""
        UPDATE business_checklist 
        SET 任务项列表 = %s
        WHERE 清单名称 = '退休教师呈报业务清单'
    """, (json.dumps(task_items, ensure_ascii=False),))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("退休业务清单已更新为规定的7项任务！")
    print("\n任务列表：")
    for task in task_items:
        print(f"{task['序号']}. {task['标题']} ({task['类型']})")

if __name__ == '__main__':
    update_checklist()
