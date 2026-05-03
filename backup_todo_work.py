"""
备份旧待办系统数据
"""
import psycopg2
import json
from datetime import datetime, date
from decimal import Decimal

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8', errors='ignore')
        return super().default(obj)

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)

cursor = conn.cursor()

print("=" * 80)
print("备份旧待办系统数据（todo_work 表）")
print("=" * 80)

# 查询所有数据
cursor.execute("""
    SELECT * FROM todo_work ORDER BY created_at
""")
rows = cursor.fetchall()

# 获取列名
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'todo_work'
    ORDER BY ordinal_position
""")
columns = [row[0] for row in cursor.fetchall()]

# 转换为字典列表
backup_data = []
for row in rows:
    data = dict(zip(columns, row))
    backup_data.append(data)

# 保存到JSON文件
backup_file = f'd:\\erp_thirteen\\todo_work_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(backup_data, f, ensure_ascii=False, indent=2, cls=CustomEncoder)

print(f"\n[OK] 已备份 {len(backup_data)} 条记录到：")
print(f"     {backup_file}")

cursor.close()
conn.close()
