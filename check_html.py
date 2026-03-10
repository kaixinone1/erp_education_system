import psycopg2
import re

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 查询HTML模板文件路径
cursor.execute("SELECT file_path, file_name FROM document_templates WHERE template_id = '职工退休呈报表html'")

row = cursor.fetchone()
if row:
    print(f'HTML模板路径: {row[0]}')
    print(f'HTML模板名称: {row[1]}')
    
    # 读取HTML文件
    try:
        with open(row[0], 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 查找单位和姓名
        if '单位' in content:
            print('\n找到 单位 字段')
        if '姓名' in content:
            print('找到 姓名 字段')
            
        # 查找包含这两个字段的具体位置
        matches = re.findall(r'.{0,50}单位.{0,50}', content)
        for match in matches[:3]:
            print(f'  ...{match}...')
            
    except Exception as e:
        print(f'读取文件失败: {e}')
else:
    print('未找到HTML模板')

cursor.close()
conn.close()
