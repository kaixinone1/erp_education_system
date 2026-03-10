import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 创建 person_tags 标签字典表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS person_tags (
        id SERIAL PRIMARY KEY,
        tag_name VARCHAR(100) NOT NULL UNIQUE,
        tag_name_cn VARCHAR(100),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 从 id_card 表获取所有标签列（排除 id, name, id_card, created_at, updated_at）
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'id_card' AND table_schema = 'public'
    ORDER BY ordinal_position
""")

columns = [row[0] for row in cursor.fetchall()]
tag_columns = [col for col in columns if col not in ['id', 'name', 'id_card', 'created_at', 'updated_at']]

print(f'发现 {len(tag_columns)} 个标签列：')
for col in tag_columns:
    print(f'  {col}')

# 将标签插入 person_tags 表
tag_mapping = {
    'salary': '基础工资',
    'performance_salary': '绩效工资',
    'subsidy': '乡镇补贴',
    'post': '岗位聘用',
    'xin_ji_zhi': '新机制',
    'year_assessment': '年度考核',
    'year': '人事年报',
    'salary_year': '工资年报',
    'xiang_cun_ding_xiang': '乡村定向',
    'retired': '延迟退休',
    'party_member': '共产党员',
    'dang_ji': '党籍',
    'league_member': '共青团员',
    'tuan_ji': '团籍',
    'masses': '群众',
    'active': '在职',
    'diao_chu': '调出',
    'diao_li': '调离',
    'ci_zhi': '辞职',
    'jie_diao': '借调',
    'li_xiu': '离退',
    'retired_1': '退休',
    'si_wang': '死亡',
    'bing_xiu': '病休',
    'bing_jia': '病假',
    'zu_zhi_guan_xi_gua_kao': '组织关系挂靠'
}

inserted_count = 0
for col in tag_columns:
    cn_name = tag_mapping.get(col, col)
    try:
        cursor.execute("""
            INSERT INTO person_tags (tag_name, tag_name_cn, description)
            VALUES (%s, %s, %s)
            ON CONFLICT (tag_name) DO NOTHING
        """, (col, cn_name, f'身份证属性标签: {cn_name}'))
        if cursor.rowcount > 0:
            inserted_count += 1
    except Exception as e:
        print(f'插入标签 {col} 失败: {e}')

conn.commit()

print(f'\n成功插入 {inserted_count} 个标签到 person_tags 表')

# 验证
cursor.execute("SELECT COUNT(*) FROM person_tags")
count = cursor.fetchone()[0]
print(f'person_tags 表现在共有 {count} 个标签')

cursor.close()
conn.close()
