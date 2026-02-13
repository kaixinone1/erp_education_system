#!/usr/bin/env python3
"""
详细检查 teacher_basic 表的情况
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 1. 检查表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'teacher_basic'
            )
        """)
        exists = cursor.fetchone()[0]
        print(f"teacher_basic 表是否存在: {exists}")
        
        if not exists:
            print("错误：teacher_basic 表不存在！")
            return
        
        # 2. 检查表结构
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'teacher_basic' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f"\nteacher_basic 表结构 ({len(columns)} 个字段):")
        print("-" * 60)
        for col_name, data_type, is_nullable in columns:
            print(f"  {col_name}: {data_type} {'(nullable)' if is_nullable == 'YES' else '(not null)'}")
        
        # 3. 检查总数据量
        cursor.execute("SELECT COUNT(*) FROM teacher_basic")
        total_count = cursor.fetchone()[0]
        print(f"\n总数据量: {total_count} 条")
        
        # 4. 检查有身份证号码的数据量
        cursor.execute("SELECT COUNT(*) FROM teacher_basic WHERE 身份证号码 IS NOT NULL AND 身份证号码 != ''")
        has_id_card = cursor.fetchone()[0]
        print(f"有身份证号码的数据: {has_id_card} 条")
        
        # 5. 检查没有身份证号码的数据量
        cursor.execute("SELECT COUNT(*) FROM teacher_basic WHERE 身份证号码 IS NULL OR 身份证号码 = ''")
        no_id_card = cursor.fetchone()[0]
        print(f"无身份证号码的数据: {no_id_card} 条")
        
        # 6. 显示前10条数据（包含身份证号码）
        print("\n前10条数据示例:")
        print("-" * 60)
        cursor.execute("SELECT id, 姓名, 身份证号码 FROM teacher_basic WHERE 身份证号码 IS NOT NULL LIMIT 10")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  ID: {row[0]}, 姓名: {row[1]}, 身份证: {row[2]}")
        
        # 7. 检查身份证号码是否有重复
        cursor.execute("""
            SELECT 身份证号码, COUNT(*) as cnt
            FROM teacher_basic
            WHERE 身份证号码 IS NOT NULL AND 身份证号码 != ''
            GROUP BY 身份证号码
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"\n警告：发现 {len(duplicates)} 个重复的身份证号码")
            for id_card, cnt in duplicates[:5]:
                print(f"  身份证 {id_card} 重复 {cnt} 次")
        else:
            print("\n身份证号码无重复")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check()
