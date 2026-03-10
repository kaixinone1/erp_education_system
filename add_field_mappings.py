import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 添加常用字段映射
mappings = [
    ('姓名', 'teacher_basic_info', 'name'),
    ('身份证号', 'teacher_basic_info', 'id_card'),
    ('性别', 'teacher_basic_info', 'gender'),
    ('出生日期', 'teacher_basic_info', 'birth_date'),
    ('参加工作时间', 'teacher_basic_info', 'work_start_date'),
    ('进单位时间', 'teacher_basic_info', 'entry_date'),
    ('单位名称', 'teacher_basic_info', 'unit_name'),
    ('编制性质', 'teacher_basic_info', 'staffing_type'),
    ('岗位', 'teacher_basic_info', 'position'),
    ('职务', 'teacher_basic_info', 'job_title'),
    ('技术等级', 'teacher_basic_info', 'technical_level'),
    ('岗位等级', 'teacher_basic_info', 'position_level'),
]

for placeholder, table, field in mappings:
    cursor.execute("""
        INSERT INTO universal_field_mapping (placeholder_name, table_name, field_name)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (placeholder, table, field))

conn.commit()
print("字段映射添加完成！")

# 验证
cursor.execute("SELECT COUNT(*) FROM universal_field_mapping")
count = cursor.fetchone()[0]
print(f"当前有 {count} 条字段映射")

cursor.close()
conn.close()
