-- 模板管理系统数据库表结构
-- 创建时间：2026-05-16

-- 模板配置表
CREATE TABLE IF NOT EXISTS template_configs (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(50) UNIQUE NOT NULL,
    template_name VARCHAR(100) NOT NULL,
    template_type VARCHAR(50),
    config_json JSONB NOT NULL,
    original_file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 字段映射表
CREATE TABLE IF NOT EXISTS template_field_mappings (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(50) REFERENCES template_configs(template_id) ON DELETE CASCADE,
    chinese_name VARCHAR(100) NOT NULL,
    english_name VARCHAR(100),
    row_number INTEGER NOT NULL,
    column_number INTEGER NOT NULL,
    data_table VARCHAR(100),
    data_field VARCHAR(100),
    transform_func VARCHAR(100),
    default_value VARCHAR(255),
    mapping_confidence FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 填报记录表
CREATE TABLE IF NOT EXISTS template_fill_records (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(50) REFERENCES template_configs(template_id) ON DELETE CASCADE,
    fill_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    query_params JSONB,
    filled_data JSONB,
    export_file_path VARCHAR(255),
    operator VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_template_configs_template_id ON template_configs(template_id);
CREATE INDEX IF NOT EXISTS idx_template_field_mappings_template_id ON template_field_mappings(template_id);
CREATE INDEX IF NOT EXISTS idx_template_fill_records_template_id ON template_fill_records(template_id);
CREATE INDEX IF NOT EXISTS idx_template_fill_records_fill_time ON template_fill_records(fill_time);

-- 添加注释（PostgreSQL支持）
COMMENT ON TABLE template_configs IS '模板配置表';
COMMENT ON COLUMN template_configs.template_id IS '模板唯一标识';
COMMENT ON COLUMN template_configs.template_name IS '模板名称（中文）';
COMMENT ON COLUMN template_configs.template_type IS '模板类型';
COMMENT ON COLUMN template_configs.config_json IS 'JSON配置内容';

COMMENT ON TABLE template_field_mappings IS '字段映射表';
COMMENT ON COLUMN template_field_mappings.chinese_name IS '中文字段名';
COMMENT ON COLUMN template_field_mappings.english_name IS '英文字段名';
COMMENT ON COLUMN template_field_mappings.row_number IS '行号';
COMMENT ON COLUMN template_field_mappings.column_number IS '列号';
COMMENT ON COLUMN template_field_mappings.data_table IS '数据源表名';
COMMENT ON COLUMN template_field_mappings.data_field IS '数据源字段名';

COMMENT ON TABLE template_fill_records IS '填报记录表';
COMMENT ON COLUMN template_fill_records.fill_time IS '填报时间';
COMMENT ON COLUMN template_fill_records.query_params IS '查询条件';
COMMENT ON COLUMN template_fill_records.filled_data IS '填报数据';
COMMENT ON COLUMN template_fill_records.operator IS '操作人';