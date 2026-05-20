-- 模板配置表
CREATE TABLE IF NOT EXISTS template_configs (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(100) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    version VARCHAR(20) DEFAULT '1.0',
    description TEXT,
    category VARCHAR(100),
    config_json JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 模板数据记录表
CREATE TABLE IF NOT EXISTS template_data_records (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    data_json JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_id, year, month)
);

-- 模板字段值表
CREATE TABLE IF NOT EXISTS template_field_values (
    id SERIAL PRIMARY KEY,
    record_id INT REFERENCES template_data_records(id) ON DELETE CASCADE,
    field_id VARCHAR(100) NOT NULL,
    field_name VARCHAR(200) NOT NULL,
    field_value TEXT,
    value_type VARCHAR(50),
    calculation_formula TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_template_configs_template_id ON template_configs(template_id);
CREATE INDEX IF NOT EXISTS idx_template_data_records_template_id ON template_data_records(template_id);
CREATE INDEX IF NOT EXISTS idx_template_data_records_year_month ON template_data_records(year, month);
CREATE INDEX IF NOT EXISTS idx_template_field_values_record_id ON template_field_values(record_id);

COMMENT ON TABLE template_configs IS '模板配置表';
COMMENT ON TABLE template_data_records IS '模板数据记录表';
COMMENT ON TABLE template_field_values IS '模板字段值表';
