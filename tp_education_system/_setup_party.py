import psycopg2

conn = psycopg2.connect(host='localhost', dbname='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 1. 在党员信息表中添加"组织关系状态"字段
party_table = 'zao_yang_shi_tai_ping_zhen_zhong_xin_xue_xiao_dang_yuan_xin_xi_'

try:
    cur.execute(f"""
        ALTER TABLE "{party_table}" 
        ADD COLUMN IF NOT EXISTS organizational_relationship_status VARCHAR(50)
    """)
    conn.commit()
    print("✅ 数据库字段 organizational_relationship_status 已添加")
except Exception as e:
    conn.rollback()
    print(f"❌ 添加字段失败: {e}")

# 2. 创建组织关系状态字典表
try:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dict_party_relation_status (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    print("✅ 字典表 dict_party_relation_status 已创建")
except Exception as e:
    conn.rollback()
    print(f"❌ 创建字典表失败: {e}")

# 3. 插入字典数据
statuses = [
    ('正常', '组织关系正常在本单位'),
    ('去世', '党员去世，终止党籍'),
    ('组织关系转出', '组织关系转到外单位'),
    ('组织关系挂靠', '组织关系暂时挂靠在本单位过渡'),
    ('开除党籍', '违纪被开除党籍'),
    ('退党/自行脱党', '主动退党或长期失联自行脱党'),
]

for name, desc in statuses:
    try:
        cur.execute(
            "INSERT INTO dict_party_relation_status (name, description) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (name, desc)
        )
    except:
        # 如果表刚创建，ON CONFLICT 可能不适用
        cur.execute(
            "SELECT id FROM dict_party_relation_status WHERE name = %s",
            (name,)
        )
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO dict_party_relation_status (name, description) VALUES (%s, %s)",
                (name, desc)
            )

conn.commit()
print("✅ 字典数据已插入")

# 验证
cur.execute("SELECT * FROM dict_party_relation_status ORDER BY id")
print("\n=== 组织关系状态字典 ===")
for row in cur.fetchall():
    print(f"  id={row[0]}, name={row[1]}, desc={row[2]}")

cur.close()
conn.close()