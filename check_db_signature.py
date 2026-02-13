#!/usr/bin/env python3
"""
检查数据库中的实际表签名
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)

def get_table_signature_from_db(table_name):
    """从数据库获取表的字段签名"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = :table_name AND table_schema = 'public'
                ORDER BY column_name
            """), {"table_name": table_name})
            
            all_columns = []
            signature = []
            for row in result:
                col_name = row[0]
                data_type = row[1]
                all_columns.append((col_name, data_type))
                
                # 跳过系统字段（原始逻辑）
                if col_name in ['id', 'created_at', 'updated_at', 'import_batch', 'code']:
                    continue
                signature.append((col_name.lower(), data_type))
            
            return all_columns, signature
    except Exception as e:
        print(f"获取表 {table_name} 签名失败: {e}")
        return None, None

all_cols, sig = get_table_signature_from_db('teacher_record')

print("teacher_record 表的所有字段:")
print("-" * 60)
for col, dtype in all_cols:
    print(f"  {col}: {dtype}")

print(f"\n过滤后的签名字段 ({len(sig)} 个):")
print("-" * 60)
for col, dtype in sig:
    print(f"  {col}: {dtype}")
