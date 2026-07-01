import sys; sys.stdout.reconfigure(encoding='utf-8')
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, database="taiping_education",
    user="taiping_user", password="taiping_password"
)
cursor = conn.cursor()

print("=== saved_exports 全部记录 ===")
cursor.execute('SELECT id, 模板id, 年月, 保存时间 FROM saved_exports ORDER BY id DESC')
for row in cursor.fetchall():
    print(f"  ID={row[0]}  模板id=[{row[1]}]  年月=[{row[2]}]  保存时间=[{row[3]}]")

print("\n=== 测试不同年月匹配 ===")
template_id = 'tpl_15cc984d'
for ym in ['2026-05', '2026年6月', '2026年5月', '2026-05-01']:
    cursor.execute('SELECT id FROM saved_exports WHERE 模板id=%s AND 年月=%s', (template_id, ym))
    rows = cursor.fetchall()
    print(f"  模板id={template_id} 年月=[{ym}] → {len(rows)}条")

print("\n=== 不传年月 ===")
cursor.execute('SELECT id, 年月 FROM saved_exports WHERE 模板id=%s ORDER BY 保存时间 DESC LIMIT 10', (template_id,))
for row in cursor.fetchall():
    print(f"  ID={row[0]}  年月=[{row[1]}]")

conn.close()