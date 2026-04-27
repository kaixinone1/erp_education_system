-- 报表模板配置系统数据库表结构
-- 创建时间: 2026-04-03

-- 1. 报表模板主表
CREATE TABLE IF NOT EXISTS report_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    template_code VARCHAR(50) UNIQUE,
    template_type VARCHAR(20) DEFAULT 'summary',
    description TEXT,
    file_format VARCHAR(20) DEFAULT 'html',
    template_file_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

COMMENT ON TABLE report_templates IS '报表模板主表';
COMMENT ON COLUMN report_templates.template_name IS '模板名称';
COMMENT ON COLUMN report_templates.template_code IS '模板编码';
COMMENT ON COLUMN report_templates.template_type IS '模板类型: summary-汇总表, individual-个人表';
COMMENT ON COLUMN report_templates.description IS '模板描述';
COMMENT ON COLUMN report_templates.file_format IS '文件格式: excel/word/html';
COMMENT ON COLUMN report_templates.template_file_path IS '模板文件路径';
COMMENT ON COLUMN report_templates.status IS '状态: active-启用, inactive-停用';
COMMENT ON COLUMN report_templates.created_by IS '创建人';
COMMENT ON COLUMN report_templates.updated_by IS '更新人';

-- 2. 报表模板字段配置表
CREATE TABLE IF NOT EXISTS report_template_fields (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES report_templates(id) ON DELETE CASCADE,
    field_name VARCHAR(50) NOT NULL,
    field_label VARCHAR(100) NOT NULL,
    field_type VARCHAR(20) DEFAULT 'text',
    placeholder VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT true,
    is_visible BOOLEAN DEFAULT true,
    width VARCHAR(20),
    format_string VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE report_template_fields IS '报表模板字段配置表';
COMMENT ON COLUMN report_template_fields.field_name IS '字段名(英文)';
COMMENT ON COLUMN report_template_fields.field_label IS '字段显示名(中文)';
COMMENT ON COLUMN report_template_fields.field_type IS '字段类型: text-文本, number-数字, calculate-计算';
COMMENT ON COLUMN report_template_fields.placeholder IS '模板中的占位符';
COMMENT ON COLUMN report_template_fields.sort_order IS '排序序号';
COMMENT ON COLUMN report_template_fields.is_enabled IS '是否启用';
COMMENT ON COLUMN report_template_fields.is_visible IS '是否可见';
COMMENT ON COLUMN report_template_fields.width IS '列宽';
COMMENT ON COLUMN report_template_fields.format_string IS '格式字符串';

-- 3. 字段数据来源配置表
CREATE TABLE IF NOT EXISTS report_field_sources (
    id SERIAL PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES report_template_fields(id) ON DELETE CASCADE,
    source_type VARCHAR(20) NOT NULL,
    source_config JSONB,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE report_field_sources IS '字段数据来源配置表';
COMMENT ON COLUMN report_field_sources.source_type IS '来源类型: tag-标签, table-数据表, dictionary-字典表, calculate-计算公式, input-手动输入';
COMMENT ON COLUMN report_field_sources.source_config IS '来源配置(JSON格式)';

-- 4. 标签筛选配置表
CREATE TABLE IF NOT EXISTS report_tag_filters (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES report_templates(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL,
    tag_name VARCHAR(50),
    logic_type VARCHAR(20) DEFAULT 'include',
    logic_operator VARCHAR(10) DEFAULT 'AND',
    sort_order INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE report_tag_filters IS '标签筛选配置表';
COMMENT ON COLUMN report_tag_filters.tag_id IS '标签ID';
COMMENT ON COLUMN report_tag_filters.tag_name IS '标签名称(冗余存储)';
COMMENT ON COLUMN report_tag_filters.logic_type IS '逻辑类型: include-包含, exclude-排除';
COMMENT ON COLUMN report_tag_filters.logic_operator IS '逻辑运算符: AND, OR';
COMMENT ON COLUMN report_tag_filters.is_required IS '是否必需';

-- 5. 计算字段配置表
CREATE TABLE IF NOT EXISTS report_calculate_fields (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES report_templates(id) ON DELETE CASCADE,
    field_name VARCHAR(50) NOT NULL,
    formula TEXT NOT NULL,
    description TEXT,
    depends_on_fields JSONB,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE report_calculate_fields IS '计算字段配置表';
COMMENT ON COLUMN report_calculate_fields.formula IS '计算公式';
COMMENT ON COLUMN report_calculate_fields.description IS '公式说明';
COMMENT ON COLUMN report_calculate_fields.depends_on_fields IS '依赖的字段列表';

-- 6. 报表数据备注记录表
CREATE TABLE IF NOT EXISTS report_data_remarks (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES report_templates(id) ON DELETE CASCADE,
    report_period VARCHAR(20),
    remark_type VARCHAR(50),
    teacher_id INTEGER,
    teacher_name VARCHAR(50),
    change_content TEXT,
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);

COMMENT ON TABLE report_data_remarks IS '报表数据备注记录表';
COMMENT ON COLUMN report_data_remarks.report_period IS '报表期间(如: 2026-04)';
COMMENT ON COLUMN report_data_remarks.remark_type IS '备注类型: tag_change-标签变更, status_change-状态变更, position_change-岗位变更';
COMMENT ON COLUMN report_data_remarks.change_content IS '变更内容';
COMMENT ON COLUMN report_data_remarks.change_reason IS '变更原因';

-- 7. 报表生成记录表
CREATE TABLE IF NOT EXISTS report_generation_logs (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES report_templates(id),
    report_period VARCHAR(20),
    generation_params JSONB,
    generated_file_path VARCHAR(500),
    generated_by VARCHAR(50),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT
);

COMMENT ON TABLE report_generation_logs IS '报表生成记录表';
COMMENT ON COLUMN report_generation_logs.generation_params IS '生成参数';
COMMENT ON COLUMN report_generation_logs.status IS '状态: success-成功, failed-失败';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_report_templates_status ON report_templates(status);
CREATE INDEX IF NOT EXISTS idx_report_templates_type ON report_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_template_fields_template_id ON report_template_fields(template_id);
CREATE INDEX IF NOT EXISTS idx_field_sources_field_id ON report_field_sources(field_id);
CREATE INDEX IF NOT EXISTS idx_tag_filters_template_id ON report_tag_filters(template_id);
CREATE INDEX IF NOT EXISTS idx_calculate_fields_template_id ON report_calculate_fields(template_id);
CREATE INDEX IF NOT EXISTS idx_data_remarks_template_id ON report_data_remarks(template_id);
CREATE INDEX IF NOT EXISTS idx_data_remarks_period ON report_data_remarks(report_period);
CREATE INDEX IF NOT EXISTS idx_generation_logs_template_id ON report_generation_logs(template_id);

-- 插入绩效审批表模板基础数据
INSERT INTO report_templates (template_name, template_code, template_type, description, file_format, template_file_path, status)
VALUES (
    '义务教育学校教职工绩效工资审批表',
    'performance_salary_approval',
    'summary',
    '教职工绩效工资审批汇总表，按岗位分类统计',
    'html',
    'templates/performance_pay/义务教育学校教职工绩效工资审批表.html',
    'active'
)
ON CONFLICT (template_code) DO NOTHING;

-- 插入绩效工资标准字典表（如果不存在）
CREATE TABLE IF NOT EXISTS performance_salary_standard (
    id SERIAL PRIMARY KEY,
    position_name VARCHAR(50) NOT NULL,
    position_level VARCHAR(20),
    salary_standard DECIMAL(10,2) NOT NULL,
    effective_date DATE,
    expiry_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(position_name, position_level, effective_date)
);

COMMENT ON TABLE performance_salary_standard IS '绩效工资标准字典表';
COMMENT ON COLUMN performance_salary_standard.position_name IS '岗位名称';
COMMENT ON COLUMN performance_salary_standard.position_level IS '岗位级别';
COMMENT ON COLUMN performance_salary_standard.salary_standard IS '月工资标准';
COMMENT ON COLUMN performance_salary_standard.effective_date IS '生效日期';
COMMENT ON COLUMN performance_salary_standard.expiry_date IS '失效日期';

-- 插入默认绩效工资标准数据
INSERT INTO performance_salary_standard (position_name, position_level, salary_standard, effective_date, status)
VALUES 
    ('高级教师', '高级', 3200.00, '2024-01-01', 'active'),
    ('一级教师', '一级', 2800.00, '2024-01-01', 'active'),
    ('二级教师', '二级', 2500.00, '2024-01-01', 'active'),
    ('三级教师', '三级', 2200.00, '2024-01-01', 'active'),
    ('管理岗位', '九级', 3000.00, '2024-01-01', 'active'),
    ('高级技师', '高级', 2600.00, '2024-01-01', 'active'),
    ('技师', '中级', 2400.00, '2024-01-01', 'active'),
    ('高级工', '高级', 2200.00, '2024-01-01', 'active'),
    ('中级工', '中级', 2000.00, '2024-01-01', 'active'),
    ('初级工', '初级', 1800.00, '2024-01-01', 'active'),
    ('普工', '普通', 1600.00, '2024-01-01', 'active')
ON CONFLICT DO NOTHING;
