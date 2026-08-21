import psycopg2

conn = psycopg2.connect(
    host='localhost', port='5432',
    database='taiping_education',
    user='taiping_user', password='taiping_password'
)
cursor = conn.cursor()

# Check 2026-08
cursor.execute("""
    SELECT id, remark_type, teacher_name, original_status, new_status, 
           original_post, new_post, change_category, change_detail
    FROM performance_pay_remarks 
    WHERE report_period = '2026-08'
    ORDER BY id
""")
rows = cursor.fetchall()
print(f"=== report_period=2026-08 共 {len(rows)} 条记录 ===")
for row in rows:
    print(f"  ID={row[0]} type={row[1]} name={row[2]} old_status={row[3]} new_status={row[4]} old_post={row[5]} new_post={row[6]} cat={row[7]} detail={row[8]}")

# Also check the saved export record to see what params were used
cursor.execute("""
    SELECT id, "查询条件", "统计范围", "填报口径", "保存时间"
    FROM saved_exports
    WHERE id = 133
""")
row = cursor.fetchone()
if row:
    print(f"\n=== 保存记录 ID=133 ===")
    print(f"  查询条件: {row[1]}")
    print(f"  统计范围: {row[2]}")
    print(f"  填报口径: {row[3]}")
    print(f"  保存时间: {row[4]}")

cursor.close()
conn.close()