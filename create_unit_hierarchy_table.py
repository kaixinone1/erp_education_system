from sqlalchemy import create_engine, text

engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')
conn = engine.connect()

# 第一步：创建unit_hierarchy表
print("第一步：创建unit_hierarchy表")
print("=" * 80)

create_table_sql = """
DROP TABLE IF EXISTS unit_hierarchy CASCADE;

CREATE TABLE unit_hierarchy (
    id SERIAL PRIMARY KEY,
    unit_level VARCHAR(20) NOT NULL,
    unit_name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES unit_hierarchy(id),
    school_dict_id INTEGER,
    full_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(unit_level, unit_name, parent_id)
);

CREATE INDEX idx_unit_hierarchy_level ON unit_hierarchy(unit_level);
CREATE INDEX idx_unit_hierarchy_parent ON unit_hierarchy(parent_id);
CREATE INDEX idx_unit_hierarchy_school_dict ON unit_hierarchy(school_dict_id);
"""

try:
    conn.execute(text(create_table_sql))
    conn.commit()
    print("[OK] unit_hierarchy表创建成功")
except Exception as e:
    print(f"[ERROR] 创建表失败：{e}")
    conn.rollback()

conn.close()
