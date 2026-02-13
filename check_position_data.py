#!/usr/bin/env python3
"""
检查教师职务字典和教师职务记录表的数据
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_data():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    try:
        # 1. 查看教师职务字典表结构
        print("=" * 80)
        print("1. 教师职务字典表 (dict_teacher_position_dictionary) 结构")
        print("=" * 80)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'dict_teacher_position_dictionary'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
        
        # 2. 查看教师职务字典表数据
        print("\n" + "=" * 80)
        print("2. 教师职务字典表数据")
        print("=" * 80)
        cursor.execute("SELECT * FROM dict_teacher_position_dictionary")
        rows = cursor.fetchall()
        print(f"  共 {len(rows)} 条数据:")
        for row in rows:
            print(f"    {row}")
        
        # 3. 查看教师职务记录表结构
        print("\n" + "=" * 80)
        print("3. 教师职务记录表 (teacher_log) 结构")
        print("=" * 80)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'teacher_log'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
        
        # 4. 查看教师职务记录表数据
        print("\n" + "=" * 80)
        print("4. 教师职务记录表数据")
        print("=" * 80)
        cursor.execute("SELECT * FROM teacher_log LIMIT 10")
        rows = cursor.fetchall()
        print(f"  共 {len(rows)} 条数据:")
        for row in rows:
            print(f"    {row}")
        
        # 5. 尝试关联查询
        print("\n" + "=" * 80)
        print("5. 关联查询测试")
        print("=" * 80)
        try:
            cursor.execute("""
                SELECT 
                    tl.id,
                    tl.姓名,
                    tl.身份证号码,
                    tl.职级,
                    dpd.职务 as 职级名称
                FROM teacher_log tl
                LEFT JOIN dict_teacher_position_dictionary dpd 
                    ON tl.职级::text = dpd.序号::text
                LIMIT 5
            """)
            rows = cursor.fetchall()
            print(f"  关联查询结果 ({len(rows)} 条):")
            for row in rows:
                print(f"    ID={row[0]}, 姓名={row[1]}, 职级={row[3]}, 职级名称={row[4]}")
        except Exception as e:
            print(f"  关联查询失败: {e}")
        
    except Exception as e:
        print(f"查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_data()
