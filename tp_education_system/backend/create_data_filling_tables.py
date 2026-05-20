from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

sql = """
-- 数据填报字段映射配置表
CREATE TABLE IF NOT EXISTS data_filling_field_mappings (
    mapping_id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL,
    field_name VARCHAR(100),
    field_position VARCHAR(20),
    source_table VARCHAR(100),
    source_field VARCHAR(100),
    stat_type VARCHAR(50) DEFAULT '直接取值',
    stat_formula TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(template_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_data_filling_field_mappings_template_id ON data_filling_field_mappings(template_id);
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()
    print("[OK] 数据填报字段映射表创建成功！")
