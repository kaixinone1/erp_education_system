-- 模板字段映射配置表
CREATE TABLE IF NOT EXISTS template_field_mappings (
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

-- 填报记录表
CREATE TABLE IF NOT EXISTS fill_records (
    record_id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL,
    fill_type VARCHAR(20),
    fill_target VARCHAR(200),
    teacher_id INTEGER,
    fill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filled_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'draft',
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(template_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_field_mappings_template_id ON template_field_mappings(template_id);
CREATE INDEX IF NOT EXISTS idx_fill_records_template_id ON fill_records(template_id);
CREATE INDEX IF NOT EXISTS idx_fill_records_teacher_id ON fill_records(teacher_id);
CREATE INDEX IF NOT EXISTS idx_fill_records_status ON fill_records(status);
