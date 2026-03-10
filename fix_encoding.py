"""
修复职工退休呈报表html模板的字段映射编码问题
"""
import psycopg2
import re

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

template_id = '职工退休呈报表html'

# 获取模板文件路径
cursor.execute("""
    SELECT file_path FROM document_templates WHERE template_id = %s
""", (template_id,))

row = cursor.fetchone()
if not row:
    print(f'模板 {template_id} 不存在')
else:
    file_path = row[0]
    
    # 尝试多种编码读取文件
    content = None
    used_encoding = None
    for encoding in ['gbk', 'gb2312', 'gb18030', 'utf-8', 'latin-1']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            print(f'使用编码 {encoding} 成功读取文件')
            break
        except UnicodeDecodeError:
            continue
    
    if content:
        # 提取占位符
        pattern = r'\{\{([^}]+)\}\}'
        placeholders = list(set(re.findall(pattern, content)))
        
        print(f'\n找到 {len(placeholders)} 个占位符:')
        for p in placeholders[:10]:
            print(f'  {p}')
        
        # 删除旧的乱码映射
        cursor.execute("""
            DELETE FROM template_field_mapping
            WHERE template_id = %s
        """, (template_id,))
        print(f'\n已删除旧的字段映射')
        
        # 创建新的正确映射
        intermediate_table = 'retirement_report_data'
        for placeholder in placeholders:
            cursor.execute("""
                INSERT INTO template_field_mapping 
                (template_id, placeholder_name, intermediate_table, intermediate_field, is_active, created_at)
                VALUES (%s, %s, %s, %s, true, NOW())
            """, (template_id, placeholder, intermediate_table, placeholder))
        
        conn.commit()
        print(f'\n已为模板 {template_id} 创建 {len(placeholders)} 个正确的字段映射')
    else:
        print('无法读取文件')

cursor.close()
conn.close()
