-- 删除已存在的表（如果存在）
DROP TABLE IF EXISTS template_usage_records;
DROP TABLE IF EXISTS template_field_mappings;
DROP TABLE IF EXISTS document_templates;

-- 创建文档模板表
CREATE TABLE document_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(50) UNIQUE NOT NULL,
    template_name VARCHAR(100) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建模板字段映射表
CREATE TABLE template_field_mappings (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(50) NOT NULL,
    field_name VARCHAR(50) NOT NULL,
    field_label VARCHAR(100),
    field_type VARCHAR(20) DEFAULT 'text',
    position_type VARCHAR(20) NOT NULL,
    position_data JSONB NOT NULL,
    default_value TEXT,
    data_source VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES document_templates(template_id) ON DELETE CASCADE
);

-- 创建模板使用记录表
CREATE TABLE template_usage_records (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(50) NOT NULL,
    business_type VARCHAR(50) NOT NULL,
    business_id INTEGER NOT NULL,
    teacher_id INTEGER,
    generated_file_path VARCHAR(255),
    generated_file_name VARCHAR(100),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(50),
    FOREIGN KEY (template_id) REFERENCES document_templates(template_id)
);

-- 创建索引
CREATE INDEX idx_template_mappings_template_id ON template_field_mappings(template_id);
CREATE INDEX idx_template_usage_template_id ON template_usage_records(template_id);
CREATE INDEX idx_template_usage_business ON template_usage_records(business_type, business_id);
