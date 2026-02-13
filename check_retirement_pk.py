#!/usr/bin/env python3
"""
检查退休呈报表数据表的主键
"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )

conn = get_db_connection()
cursor = conn.cursor()

# 检查主键
cursor.execute("""
    SELECT kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
    WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_name = 'retirement_report_data'
""")

pk = cursor.fetchone()
print(f"主键: {pk[0] if pk else '无'}")

# 检查唯一约束
cursor.execute("""
    SELECT tc.constraint_name, kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
    WHERE tc.constraint_type = 'UNIQUE'
        AND tc.table_name = 'retirement_report_data'
""")

unique_constraints = cursor.fetchall()
print(f"\n唯一约束:")
for uc in unique_constraints:
    print(f"  {uc[0]}: {uc[1]}")

cursor.close()
conn.close()
