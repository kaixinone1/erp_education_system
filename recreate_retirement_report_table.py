#!/usr/bin/env python3
"""
严格按照指定字段重新创建退休呈报数据表（中间表）
"""
import psycopg2

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def recreate_table():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 删除旧表
    cursor.execute("DROP TABLE IF EXISTS retirement_report_data CASCADE")
    print("旧表已删除")
    
    # 严格按照指定字段创建新表
    create_sql = """
        CREATE TABLE retirement_report_data (
            id SERIAL PRIMARY KEY,
            teacher_id INTEGER,
            template_id INTEGER,
            -- 基本信息
            身份证号码 VARCHAR(18),
            岗位 VARCHAR(100),
            姓名 VARCHAR(50),
            性别 VARCHAR(10),
            出生日期 DATE,
            民族 VARCHAR(20),
            文化程度 VARCHAR(50),
            是否独生子女 BOOLEAN,
            入党年月 VARCHAR(20),
            职务 VARCHAR(100),
            技术职称 VARCHAR(100),
            参加工作时间 DATE,
            工作年限 INTEGER,
            籍贯 VARCHAR(100),
            现住址 TEXT,
            退休原因 TEXT,
            退休后居住地址 TEXT,
            退休时间 DATE,
            -- 岗位信息1
            事业管理岗位1 VARCHAR(100),
            对应原职务1 VARCHAR(100),
            薪级1 VARCHAR(50),
            -- 岗位信息2
            事业专技岗位2 VARCHAR(100),
            对应原职务2 VARCHAR(100),
            薪级2 VARCHAR(50),
            -- 岗位信息3
            事业工勤岗位3 VARCHAR(100),
            对应技术等级3 VARCHAR(100),
            薪级3 VARCHAR(50),
            -- 职务升降
            最后一次职务升降时间 DATE,
            -- 岗位信息4
            事业管理岗位4 VARCHAR(100),
            对应原职务4 VARCHAR(100),
            薪级4 VARCHAR(50),
            -- 岗位信息5
            事业专技岗位5 VARCHAR(100),
            对应原职务5 VARCHAR(100),
            薪级5 VARCHAR(50),
            -- 岗位信息6
            事业工勤岗位6 VARCHAR(100),
            对应技术等级6 VARCHAR(100),
            薪级6 VARCHAR(50),
            -- 退休时岗位信息7
            退休时事业管理岗位7 VARCHAR(100),
            对应原职务7 VARCHAR(100),
            薪级7 VARCHAR(50),
            -- 退休时岗位信息8
            退休时事业专技岗位8 VARCHAR(100),
            对应原职务8 VARCHAR(100),
            薪级8 VARCHAR(50),
            -- 退休时岗位信息9
            退休时事业工勤岗位9 VARCHAR(100),
            对应技术等级9 VARCHAR(100),
            薪级9 VARCHAR(50),
            -- 工作经历
            自何年何月 VARCHAR(50),
            至何年何月 VARCHAR(50),
            所在单位及职务 TEXT,
            证明人及住址 TEXT,
            -- 其他
            直系亲属供养情况 TEXT,
            备注 TEXT,
            -- 时间戳
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    cursor.execute(create_sql)
    print("新表已创建")
    
    # 创建索引
    cursor.execute("CREATE INDEX idx_retirement_teacher_id ON retirement_report_data(teacher_id)")
    cursor.execute("CREATE INDEX idx_retirement_template_id ON retirement_report_data(template_id)")
    print("索引已创建")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("\n退休呈报数据表重建完成！")
    
    # 验证字段
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'retirement_report_data'
        ORDER BY ordinal_position
    """)
    columns = [row[0] for row in cursor.fetchall()]
    print(f"\n表字段数量: {len(columns)}")
    print("字段列表:")
    for col in columns:
        print(f"  - {col}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    recreate_table()
