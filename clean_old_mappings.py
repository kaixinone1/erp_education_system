import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 删除旧的HTML版本字段映射
old_template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm'
new_template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表docx'

cursor.execute("""
    DELETE FROM template_field_mappings 
    WHERE template_id = %s
""", (old_template_id,))

deleted_count = cursor.rowcount
print(f'删除了 {deleted_count} 个旧字段映射（HTML版本）')

# 检查新的Word版本是否有字段映射
cursor.execute("""
    SELECT COUNT(*) FROM template_field_mappings 
    WHERE template_id = %s
""", (new_template_id,))

count = cursor.fetchone()[0]
print(f'新Word版本有 {count} 个字段映射')

conn.commit()
cursor.close()
conn.close()

print('清理完成')
