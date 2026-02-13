#!/usr/bin/env python3
"""更新退休呈报表字段为中文标签"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def update():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 添加字段注释（中文标签）
    comments = {
        "teacher_id": "教师ID",
        "teacher_name": "教师姓名",
        "gender": "性别",
        "birth_date": "出生日期",
        "id_card": "身份证号",
        "ethnicity": "民族",
        "native_place": "籍贯",
        "education": "学历",
        "graduation_school": "毕业学校",
        "major": "专业",
        "degree": "学位",
        "work_start_date": "参加工作时间",
        "work_unit": "工作单位",
        "position": "职务",
        "title": "职称",
        "age": "年龄",
        "work_years": "工作年限",
        "retirement_date": "退休日期",
        "contact_phone": "联系电话"
    }
    
    for field, label in comments.items():
        try:
            cursor.execute(f"""
                COMMENT ON COLUMN retirement_report_form.{field} IS '{label}'
            """)
            print(f"已添加注释: {field} -> {label}")
        except Exception as e:
            print(f"添加注释失败 {field}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("\n字段标签更新完成！")

if __name__ == '__main__':
    update()
