import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 读取当前映射
cursor.execute("SELECT placeholder_name FROM universal_field_mapping")
existing = set([row[0] for row in cursor.fetchall()])
print(f"已有映射: {existing}")

# 添加更多字段映射（针对退休呈报表）
mappings = [
    # 基本信息
    ('姓名', 'teacher_basic_info', 'name'),
    ('性别', 'teacher_basic_info', 'gender'),
    ('出生年月', 'teacher_basic_info', 'birth_date'),
    ('民族', 'teacher_basic_info', 'nation'),
    ('籍贯', 'teacher_basic_info', 'native_place'),
    ('身份证号', 'teacher_basic_info', 'id_card'),
    
    # 工作信息
    ('参加工作时间', 'teacher_basic_info', 'work_start_date'),
    ('工作年限', 'teacher_basic_info', 'work_years'),
    ('文化程度', 'teacher_basic_info', 'education'),
    ('技术职称', 'teacher_basic_info', 'technical_title'),
    ('入党年月', 'teacher_basic_info', 'party_join_date'),
    
    # 单位信息
    ('单位名称', 'teacher_basic_info', 'unit_name'),
    ('现住址', 'teacher_basic_info', 'current_address'),
    ('在何单位任何职', 'teacher_basic_info', 'current_position'),
    ('证明人及其住址', 'teacher_basic_info', 'witness_info'),
    
    # 退休相关
    ('退休原因', 'retirement_report_data', 'retirement_reason'),
    ('是否独生子女', 'retirement_report_data', 'is_only_child'),
    ('直系亲属信息', 'retirement_report_data', 'family_info'),
    ('自何年何月', 'retirement_report_data', 'start_date'),
    ('至何年何月', 'retirement_report_data', 'end_date'),
    
    # 职务岗位（动态字段，需要根据实际表结构调整）
    ('职务', 'retirement_report_data', '职务'),
    ('职务1', 'retirement_report_data', '职务1'),
    ('职务2', 'retirement_report_data', '职务2'),
    ('职务3', 'retirement_report_data', '职务3'),
    ('岗位', 'retirement_report_data', '岗位'),
    ('岗位1', 'retirement_report_data', '岗位1'),
    ('岗位2', 'retirement_report_data', '岗位2'),
    ('岗位3', 'retirement_report_data', '岗位3'),
    ('薪级', 'retirement_report_data', '薪级'),
    ('薪级1', 'retirement_report_data', '薪级1'),
    ('薪级2', 'retirement_report_data', '薪级2'),
    ('薪级3', 'retirement_report_data', '薪级3'),
    
    # 职务升降表专用
    ('个人编号', 'teacher_basic_info', 'employee_no'),
    ('事业管理岗位1', 'retirement_report_data', '事业管理岗位1'),
    ('事业管理岗位4', 'retirement_report_data', '事业管理岗位4'),
    ('事业专技岗位2', 'retirement_report_data', '事业专技岗位2'),
    ('事业专技岗位5', 'retirement_report_data', '事业专技岗位5'),
    ('事业工勤岗位3', 'retirement_report_data', '事业工勤岗位3'),
    ('事业工勤岗位6', 'retirement_report_data', '事业工勤岗位6'),
]

added = 0
for placeholder, table, field in mappings:
    if placeholder not in existing:
        cursor.execute("""
            INSERT INTO universal_field_mapping (placeholder_name, table_name, field_name)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (placeholder, table, field))
        added += 1

conn.commit()
print(f"新增映射: {added} 条")

# 验证
cursor.execute("SELECT COUNT(*) FROM universal_field_mapping")
count = cursor.fetchone()[0]
print(f"当前共有 {count} 条字段映射")

cursor.close()
conn.close()
