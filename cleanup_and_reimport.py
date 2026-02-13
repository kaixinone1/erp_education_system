#!/usr/bin/env python3
"""
清理旧表并重新导入
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

try:
    print("=" * 80)
    print("清理旧表")
    print("=" * 80)
    
    # 删除旧的人才类型表
    old_tables = ['dict_teacher_info']
    
    for table in old_tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"  删除表: {table}")
    
    conn.commit()
    print("\n清理完成！")
    
    print("\n" + "=" * 80)
    print("现在可以重新导入数据了")
    print("=" * 80)
    print("\n请使用数据导入工作台重新导入'教师人才类型'数据")
    print("V3导入服务会自动：")
    print("  1. 创建 teacher_talent_type 表")
    print("  2. 自动关联 dict_talent_type 字典表")
    print("  3. 正确显示中文名称（高层次人才/普通人才）")
    
finally:
    cursor.close()
    conn.close()
