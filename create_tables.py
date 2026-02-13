#!/usr/bin/env python3
"""创建业务清单相关表"""
import psycopg2
import json

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def create_tables():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 创建业务清单主表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_checklist (
            id SERIAL PRIMARY KEY,
            清单名称 VARCHAR(255) NOT NULL,
            触发条件 JSONB,
            任务项列表 JSONB,
            是否有效 BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建待办工作项表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todo_work_items (
            id SERIAL PRIMARY KEY,
            教师ID INTEGER,
            清单ID INTEGER,
            清单名称 VARCHAR(255),
            教师姓名 VARCHAR(100),
            任务项列表 JSONB,
            总任务数 INTEGER DEFAULT 0,
            已完成数 INTEGER DEFAULT 0,
            状态 VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建退休证签发记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS retirement_cert_records (
            id SERIAL PRIMARY KEY,
            教师ID INTEGER,
            教师姓名 VARCHAR(100),
            签收人 VARCHAR(100),
            签收日期 DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 检查是否已存在退休教师呈报业务清单
    cursor.execute("SELECT id FROM business_checklist WHERE 清单名称 = '退休教师呈报业务清单'")
    if not cursor.fetchone():
        # 插入退休教师呈报业务清单
        任务项列表 = [
            {
                "序号": 1,
                "标题": "填报《退休待遇审批表》",
                "类型": "内部表",
                "目标": "retirement_treatment_approval",
                "参数": {"prefill_rules": ["教师姓名", "身份证号"]},
                "完成状态": False
            },
            {
                "序号": 2,
                "标题": "填报《湖北省机关事业单位养老保险待遇申报表》",
                "类型": "外部链接",
                "目标": "https://zwfw.hubei.gov.cn/",
                "参数": {},
                "完成状态": False
            },
            {
                "序号": 3,
                "标题": "填报《退休人员住房补贴审批表》",
                "类型": "内部表",
                "目标": "housing_subsidy_approval",
                "参数": {"prefill_rules": ["教师姓名", "身份证号"]},
                "完成状态": False
            },
            {
                "序号": 4,
                "标题": "填报《机关事业单位职业年金支付申报表》",
                "类型": "外部链接",
                "目标": "https://zwfw.hubei.gov.cn/",
                "参数": {},
                "完成状态": False
            },
            {
                "序号": 5,
                "标题": "填报《退休人员绩效工资审批表》",
                "类型": "自动汇总",
                "目标": "performance_pay_approval",
                "参数": {"汇总规则": "根据职务级别自动计算"},
                "完成状态": False
            },
            {
                "序号": 6,
                "标题": "签发《退休证》",
                "类型": "签发证件",
                "目标": "retirement_cert_records",
                "参数": {},
                "完成状态": False
            },
            {
                "序号": 7,
                "标题": "填报《机关事业单位退休人员一次性退休补贴申报表》",
                "类型": "内部表",
                "目标": "retirement_subsidy_application",
                "参数": {"prefill_rules": ["教师姓名", "身份证号"]},
                "完成状态": False
            }
        ]
        
        cursor.execute("""
            INSERT INTO business_checklist (清单名称, 触发条件, 任务项列表, 是否有效)
            VALUES (%s, %s, %s, %s)
        """, (
            '退休教师呈报业务清单',
            json.dumps({"source_status": "在职", "target_status": "退休"}),
            json.dumps(任务项列表),
            True
        ))
        print("已插入退休教师呈报业务清单")
    else:
        print("退休教师呈报业务清单已存在")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("表创建成功！")

if __name__ == '__main__':
    create_tables()
