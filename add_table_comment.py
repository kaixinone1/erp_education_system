#!/usr/bin/env python3
"""添加表的中文注释"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def add():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 添加表注释
    table_comments = {
        "retirement_report_form": "职工退休呈报表",
        "teacher_basic_info": "教师基本信息表",
        "teacher_education_record": "教师教育经历表",
        "teacher_position_record": "教师职务信息表",
        "teacher_title_record": "教师职称信息表",
        "teacher_work_unit": "教师工作单位表"
    }
    
    for table, comment in table_comments.items():
        try:
            cursor.execute(f"""
                COMMENT ON TABLE {table} IS '{comment}'
            """)
            print(f"已添加表注释: {table} -> {comment}")
        except Exception as e:
            print(f"添加表注释失败 {table}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("\n表注释添加完成！")

if __name__ == '__main__':
    add()
