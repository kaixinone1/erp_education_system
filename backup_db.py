#!/usr/bin/env python3
"""
使用Python备份数据库表结构和数据
"""

import psycopg2
import json
import os
from datetime import datetime

BACKUP_DIR = r'd:\erp_thirteen\backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs(BACKUP_DIR, exist_ok=True)

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

print("=" * 80)
print("备份数据库表结构和数据")
print("=" * 80)

conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

# 获取所有表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")

tables = [row[0] for row in cursor.fetchall()]
print(f"\n找到 {len(tables)} 个表")

backup_data = {}

for table in tables:
    print(f"\n备份表: {table}")
    
    # 获取表结构
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position
    """, (table,))
    
    columns = []
    for row in cursor.fetchall():
        columns.append({
            'name': row[0],
            'type': row[1],
            'nullable': row[2],
            'default': row[3]
        })
    
    # 获取表数据
    try:
        cursor.execute(f'SELECT * FROM "{table}"')
        rows = cursor.fetchall()
        
        # 获取列名
        col_names = [desc[0] for desc in cursor.description]
        
        # 转换为字典列表
        data = []
        for row in rows:
            row_dict = {}
            for i, col_name in enumerate(col_names):
                row_dict[col_name] = row[i]
            data.append(row_dict)
        
        backup_data[table] = {
            'structure': columns,
            'data': data,
            'row_count': len(data)
        }
        
        print(f"  ✓ 结构: {len(columns)} 个字段")
        print(f"  ✓ 数据: {len(data)} 条记录")
    except Exception as e:
        print(f"  ✗ 备份失败: {e}")
        backup_data[table] = {
            'structure': columns,
            'data': [],
            'row_count': 0,
            'error': str(e)
        }

# 保存备份文件
backup_file = os.path.join(BACKUP_DIR, 'database_backup.json')
with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)

cursor.close()
conn.close()

print("\n" + "=" * 80)
print(f"数据库备份完成!")
print(f"备份文件: {backup_file}")
print(f"总计: {len(tables)} 个表")
print("=" * 80)
