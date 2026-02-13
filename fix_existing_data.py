#!/usr/bin/env python3
"""
修复已导入数据的学历类型和学历字段，将整数转换为字符串
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def fix():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    print("修复 teacher_record 表的学历类型和学历字段...")
    print("=" * 80)
    
    # 1. 检查当前数据类型
    cursor.execute("""
        SELECT DISTINCT 学历类型, 学历 
        FROM teacher_record 
        ORDER BY 学历类型, 学历
    """)
    print("\n修复前的数据:")
    for row in cursor.fetchall():
        print(f"  学历类型: {row[0]} (类型: {type(row[0])}), 学历: {row[1]} (类型: {type(row[1])})")
    
    # 2. 更新学历类型字段，将整数转换为字符串
    cursor.execute("""
        UPDATE teacher_record 
        SET 学历类型 = CAST(学历类型 AS VARCHAR)
        WHERE 学历类型 IS NOT NULL
    """)
    
    # 3. 更新学历字段，将整数转换为字符串
    cursor.execute("""
        UPDATE teacher_record 
        SET 学历 = CAST(学历 AS VARCHAR)
        WHERE 学历 IS NOT NULL
    """)
    
    conn.commit()
    
    # 4. 检查修复后的数据
    cursor.execute("""
        SELECT DISTINCT 学历类型, 学历 
        FROM teacher_record 
        ORDER BY 学历类型, 学历
    """)
    print("\n修复后的数据:")
    for row in cursor.fetchall():
        print(f"  学历类型: {row[0]} (类型: {type(row[0])}), 学历: {row[1]} (类型: {type(row[1])})")
    
    # 5. 验证与字典表的关联
    print("\n验证与字典表的关联:")
    
    # 学历类型关联
    cursor.execute("""
        SELECT tr.学历类型, ed.类型名称, COUNT(*) as cnt
        FROM teacher_record tr
        LEFT JOIN education_dictionary ed ON tr.学历类型 = ed.学历类型
        GROUP BY tr.学历类型, ed.类型名称
        ORDER BY tr.学历类型
    """)
    print("\n学历类型关联:")
    for row in cursor.fetchall():
        print(f"  学历类型 {row[0]} -> {row[1]}: {row[2]} 条")
    
    # 学历关联
    cursor.execute("""
        SELECT tr.学历, ded.学历 as 学历名称, COUNT(*) as cnt
        FROM teacher_record tr
        LEFT JOIN dict_education_dictionary ded ON tr.学历 = ded.code
        GROUP BY tr.学历, ded.学历
        ORDER BY tr.学历
    """)
    print("\n学历关联:")
    for row in cursor.fetchall():
        print(f"  学历 {row[0]} -> {row[1]}: {row[2]} 条")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("修复完成！")

if __name__ == "__main__":
    fix()
