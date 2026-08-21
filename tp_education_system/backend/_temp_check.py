import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 1. 汇总表字段
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'party_member_info_summary' ORDER BY ordinal_position")
print("=== 汇总表字段 ===")
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]})")

# 2. 备份表字段
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'party_member_info_summary_backup_2026_08' ORDER BY ordinal_position")
print("\n=== 月度备份表字段 ===")
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]})")

# 3. 汇总表数据
cur.execute("SELECT * FROM party_member_info_summary ORDER BY id")
print("\n=== 汇总表数据 ===")
for r in cur.fetchall():
    print(f"  {r}")

cur.close()
conn.close()