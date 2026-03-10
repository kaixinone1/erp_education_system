"""
修复导航菜单和待办工作数据库表
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

# 删除旧表（如果存在）
cursor.execute("DROP TABLE IF EXISTS todo_work_items CASCADE")
cursor.execute("DROP TABLE IF EXISTS navigation_modules CASCADE")

# 1. 创建导航菜单表
cursor.execute("""
    CREATE TABLE navigation_modules (
        id SERIAL PRIMARY KEY,
        module_id VARCHAR(100) UNIQUE NOT NULL,
        title VARCHAR(200) NOT NULL,
        icon VARCHAR(100),
        path VARCHAR(200),
        type VARCHAR(50) DEFAULT 'module',
        parent_id VARCHAR(100) DEFAULT NULL,
        sort_order INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 2. 创建待办工作表
cursor.execute("""
    CREATE TABLE todo_work_items (
        id SERIAL PRIMARY KEY,
        title VARCHAR(500) NOT NULL,
        description TEXT,
        module_id VARCHAR(100),
        teacher_id INTEGER,
        status VARCHAR(50) DEFAULT 'pending',
        priority VARCHAR(50) DEFAULT 'normal',
        due_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 3. 插入默认导航菜单数据
navigation_data = [
    # 系统管理模块
    ('system', '系统管理', 'Setting', '/system', 'module', None, 1),
    ('system-modules', '模块管理', 'Grid', '/system/module-mgt', 'component', 'system', 1),
    ('system-tables', '数据表管理', 'List', '/system/table-mgt', 'component', 'system', 2),
    ('system-dictionaries', '字典管理', 'Folder', '/system/dictionaries', 'module', 'system', 3),
    ('system-checklist', '清单管理', 'List', '/system/checklist', 'module', 'system', 4),
    
    # 导入工作台
    ('import', '导入工作台', 'Upload', '/import', 'module', None, 2),
    ('import-workbench', '导入工作台', 'Monitor', '/import/workbench', 'component', 'import', 1),
    
    # 模板管理
    ('templates', '模板管理', 'Document', '/templates', 'module', None, 3),
    ('templates-list', '模板列表', 'List', '/templates/list', 'component', 'templates', 1),
    ('templates-upload', '上传模板', 'Upload', '/templates/upload', 'component', 'templates', 2),
]

for item in navigation_data:
    cursor.execute("""
        INSERT INTO navigation_modules (module_id, title, icon, path, type, parent_id, sort_order)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, item)

# 4. 插入示例待办工作
todo_items = [
    ('待审核的职工退休申请', '有3条职工退休申请需要审核', 'retirement', None, 'pending', 'high'),
    ('待处理的职务升降申报', '有2条职务升降申报需要处理', 'promotion', None, 'pending', 'normal'),
    ('待确认的信息变更', '有5条教师信息变更需要确认', 'info_change', None, 'pending', 'normal'),
]

for item in todo_items:
    cursor.execute("""
        INSERT INTO todo_work_items (title, description, module_id, teacher_id, status, priority)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, item)

conn.commit()
cursor.close()
conn.close()

print("导航菜单和待办工作表修复完成")
print(f"- 导航模块: {len(navigation_data)} 个")
print(f"- 待办工作: {len(todo_items)} 条")
