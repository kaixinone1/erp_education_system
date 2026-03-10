"""
从 navigation.json 迁移菜单到数据库
"""
import json
import psycopg2

# 读取 navigation.json
with open('config/navigation.json', 'r', encoding='utf-8') as f:
    nav_data = json.load(f)

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 清空现有数据
cursor.execute("DELETE FROM navigation_modules")

def insert_module(module, parent_id=None, sort_order=0):
    """递归插入模块"""
    module_id = module.get('id')
    title = module.get('title')
    icon = module.get('icon', 'Document')
    path = module.get('path', '')
    type_ = module.get('type', 'component')
    
    cursor.execute("""
        INSERT INTO navigation_modules 
        (module_id, title, icon, path, type, parent_id, sort_order)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (module_id, title, icon, path, type_, parent_id, sort_order))
    
    # 递归处理子菜单
    children = module.get('children', [])
    for i, child in enumerate(children):
        insert_module(child, module_id, i)

# 插入所有模块
for i, module in enumerate(nav_data.get('modules', [])):
    insert_module(module, None, i)

conn.commit()
cursor.close()
conn.close()

print("导航菜单迁移完成")
print(f"共迁移 {len(nav_data.get('modules', []))} 个主模块")
