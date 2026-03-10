"""
为职工退休呈报表html模板创建默认字段映射
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

template_id = '职工退休呈报表html'

# 获取模板中的占位符
cursor.execute("""
    SELECT file_path FROM document_templates WHERE template_id = %s
""", (template_id,))

row = cursor.fetchone()
if not row:
    print(f'模板 {template_id} 不存在')
else:
    file_path = row[0]
    
    # 读取HTML文件提取占位符
    import re
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        pattern = r'\{\{([^}]+)\}\}'
        placeholders = list(set(re.findall(pattern, content)))
        
        print(f'找到 {len(placeholders)} 个占位符:')
        for p in placeholders[:10]:
            print(f'  {p}')
        
        # 为每个占位符创建字段映射
        intermediate_table = 'retirement_report_data'
        
        for placeholder in placeholders:
            # 检查是否已存在映射
            cursor.execute("""
                SELECT id FROM template_field_mapping
                WHERE template_id = %s AND placeholder_name = %s
            """, (template_id, placeholder))
            
            if not cursor.fetchone():
                # 创建映射，占位符名称直接对应中间表字段名
                cursor.execute("""
                    INSERT INTO template_field_mapping 
                    (template_id, placeholder_name, intermediate_table, intermediate_field, is_active, created_at)
                    VALUES (%s, %s, %s, %s, true, NOW())
                """, (template_id, placeholder, intermediate_table, placeholder))
                print(f'  创建映射: {placeholder} -> {intermediate_table}.{placeholder}')
        
        conn.commit()
        print(f'\n已为模板 {template_id} 创建 {len(placeholders)} 个字段映射')
        
    except Exception as e:
        print(f'错误: {e}')

cursor.close()
conn.close()
