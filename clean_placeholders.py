import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 获取模板ID
template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表docx'

# 查询该模板的所有占位符
cursor.execute("""
    SELECT id, placeholder_name, created_at 
    FROM template_placeholders 
    WHERE template_id = %s 
    ORDER BY created_at DESC
""", (template_id,))

rows = cursor.fetchall()

print(f'模板 {template_id} 的占位符:')
print(f'总共 {len(rows)} 个')

# 保留最新的，删除旧的
if len(rows) > 0:
    # 获取最新的创建时间
    latest_time = rows[0][2]
    print(f'最新时间: {latest_time}')
    
    # 删除旧的占位符
    cursor.execute("""
        DELETE FROM template_placeholders 
        WHERE template_id = %s AND created_at < %s
    """, (template_id, latest_time))
    
    deleted_count = cursor.rowcount
    print(f'删除了 {deleted_count} 个旧占位符')
    
    conn.commit()
    print('清理完成')
else:
    print('没有找到占位符')

cursor.close()
conn.close()
