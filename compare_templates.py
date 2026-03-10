import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 检查两个模板的字段
templates = [
    '职工退休呈报表html',
    '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表html'
]

for template_id in templates:
    print(f'\n=== 模板: {template_id} ===')
    
    # 获取模板信息
    cursor.execute("""
        SELECT * FROM document_templates 
        WHERE template_id = %s
    """, (template_id,))
    
    row = cursor.fetchone()
    if row:
        # 获取列名
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'document_templates'
        """)
        columns = [col[0] for col in cursor.fetchall()]
        
        print('字段:')
        for i, col in enumerate(columns):
            if i < len(row):
                print(f'  {col}: {row[i]}')
    else:
        print('模板不存在')

cursor.close()
conn.close()
