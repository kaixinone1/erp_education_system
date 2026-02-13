#!/usr/bin/env python3
"""添加测试教师数据"""
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
    
    # 添加王军锋
    cursor.execute("""
        INSERT INTO teacher_basic_info (name, id_card, archive_birth_date, ethnicity, native_place, contact_phone, work_start_date, entry_date, employment_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_card) DO NOTHING
        RETURNING id
    """, ('王军锋', '420683196909152209', '1969-09-15', '汉族', '湖北省襄阳市', '13800138000', '1996-08-01', '1996-08-01', '在职'))
    
    result = cursor.fetchone()
    if result:
        teacher_id = result[0]
        print(f"添加教师成功，ID: {teacher_id}")
        
        # 添加教育经历
        cursor.execute("""
            INSERT INTO teacher_education_record (teacher_id, education_level, graduation_school, major, degree, graduation_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (teacher_id, '本科', '湖北大学', '教育学', '学士', '1996-06-30'))
        print("添加教育经历成功")
        
        # 添加职务信息
        cursor.execute("""
            INSERT INTO teacher_position_record (teacher_id, position_name, appointment_date, is_current)
            VALUES (%s, %s, %s, %s)
        """, (teacher_id, '高级教师', '2010-09-01', True))
        print("添加职务信息成功")
    else:
        print("教师已存在或添加失败")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    add()
