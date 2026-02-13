#!/usr/bin/env python3
"""
检查字典表和导入数据的关联情况
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # 1. 检查所有字典表
    print("=" * 80)
    print("检查字典表")
    print("=" * 80)
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%dict%'
        ORDER BY table_name
    """)
    dict_tables = [row[0] for row in cursor.fetchall()]
    print(f"\n找到 {len(dict_tables)} 个字典表:")
    for t in dict_tables:
        print(f"  - {t}")
    
    # 2. 检查 education_dictionary 表
    print("\n" + "=" * 80)
    print("education_dictionary 表内容:")
    print("=" * 80)
    
    cursor.execute("SELECT * FROM education_dictionary LIMIT 20")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    
    print(f"列名: {col_names}")
    print(f"数据条数: {len(rows)}")
    for row in rows:
        print(f"  {row}")
    
    # 3. 检查 dict_education_dictionary 表
    print("\n" + "=" * 80)
    print("dict_education_dictionary 表内容:")
    print("=" * 80)
    
    cursor.execute("SELECT * FROM dict_education_dictionary LIMIT 20")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    
    print(f"列名: {col_names}")
    print(f"数据条数: {len(rows)}")
    for row in rows:
        print(f"  {row}")
    
    # 4. 检查 teacher_record 表的学历类型和学历字段值
    print("\n" + "=" * 80)
    print("teacher_record 表的学历类型和学历字段值:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT DISTINCT 学历类型, 学历 
        FROM teacher_record 
        ORDER BY 学历类型, 学历
    """)
    rows = cursor.fetchall()
    
    print(f"不同的学历类型和学历组合 ({len(rows)} 种):")
    for row in rows:
        print(f"  学历类型: {row[0]}, 学历: {row[1]}")
    
    # 5. 统计各学历类型的数量
    print("\n" + "=" * 80)
    print("各学历类型的数量:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 学历类型, COUNT(*) as cnt
        FROM teacher_record
        GROUP BY 学历类型
        ORDER BY 学历类型
    """)
    
    for row in cursor.fetchall():
        print(f"  学历类型 {row[0]}: {row[1]} 条")
    
    # 6. 统计各学历的数量
    print("\n" + "=" * 80)
    print("各学历的数量:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 学历, COUNT(*) as cnt
        FROM teacher_record
        GROUP BY 学历
        ORDER BY 学历
    """)
    
    for row in cursor.fetchall():
        print(f"  学历 {row[0]}: {row[1]} 条")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check()
