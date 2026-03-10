import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 创建过滤条件模板表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS filter_condition_templates (
        id SERIAL PRIMARY KEY,
        category VARCHAR(50) NOT NULL,  -- 类别：行政管理人员、专业技术人员、工人
        name VARCHAR(100) NOT NULL,     -- 显示名称：副处级、高级教师等
        field_name VARCHAR(100) NOT NULL,  -- 字段名：行政级别、职称、技术等级
        field_value VARCHAR(100) NOT NULL, -- 字段值：副处级、高级教师
        filter_condition VARCHAR(500) NOT NULL, -- 完整的过滤条件：行政级别='副处级'
        sort_order INTEGER DEFAULT 0,   -- 排序
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 插入预定义的过滤条件
default_conditions = [
    # 行政管理人员
    ('行政管理人员', '副处级', '行政级别', '副处级', "行政级别='副处级'", 1),
    ('行政管理人员', '正科级', '行政级别', '正科级', "行政级别='正科级'", 2),
    ('行政管理人员', '副科级', '行政级别', '副科级', "行政级别='副科级'", 3),
    ('行政管理人员', '科员级', '行政级别', '科员级', "行政级别='科员级'", 4),
    ('行政管理人员', '办事员级', '行政级别', '办事员级', "行政级别='办事员级'", 5),
    # 专业技术人员
    ('专业技术人员', '正高级', '职称', '正高级', "职称='正高级'", 1),
    ('专业技术人员', '高级教师', '职称', '高级教师', "职称='高级教师'", 2),
    ('专业技术人员', '一级教师', '职称', '一级教师', "职称='一级教师'", 3),
    ('专业技术人员', '二级教师', '职称', '二级教师', "职称='二级教师'", 4),
    ('专业技术人员', '三级教师', '职称', '三级教师', "职称='三级教师'", 5),
    # 工人
    ('工人', '高级技师', '技术等级', '高级技师', "技术等级='高级技师'", 1),
    ('工人', '技师', '技术等级', '技师', "技术等级='技师'", 2),
    ('工人', '高级工', '技术等级', '高级工', "技术等级='高级工'", 3),
    ('工人', '中级工', '技术等级', '中级工', "技术等级='中级工'", 4),
    ('工人', '初级工', '技术等级', '初级工', "技术等级='初级工'", 5),
    ('工人', '普工', '技术等级', '普工', "技术等级='普工'", 6),
]

# 检查是否已有数据
cursor.execute("SELECT COUNT(*) FROM filter_condition_templates")
count = cursor.fetchone()[0]

if count == 0:
    for cond in default_conditions:
        cursor.execute("""
            INSERT INTO filter_condition_templates 
            (category, name, field_name, field_value, filter_condition, sort_order)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, cond)
    print(f'已插入 {len(default_conditions)} 个默认过滤条件')
else:
    print(f'过滤条件表已有 {count} 条数据，跳过插入')

conn.commit()

# 查看表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'filter_condition_templates'
    ORDER BY ordinal_position
""")

print('\n表结构:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# 查看数据
cursor.execute("SELECT category, name, filter_condition FROM filter_condition_templates ORDER BY category, sort_order")
print('\n过滤条件列表:')
for row in cursor.fetchall():
    print(f'  [{row[0]}] {row[1]}: {row[2]}')

cursor.close()
conn.close()
print('\n过滤条件模板表创建完成！')
