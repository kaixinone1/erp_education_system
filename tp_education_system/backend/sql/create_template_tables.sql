-- 通用模板自动填报系统数据库表

-- 1. 模板配置表
CREATE TABLE IF NOT EXISTS template_configs (
    id SERIAL PRIMARY KEY,
    模板ID VARCHAR(50) UNIQUE NOT NULL,
    模板名称 VARCHAR(100) NOT NULL,
    模板类型 VARCHAR(50),
    配置JSON JSONB NOT NULL,
    原始文件路径 VARCHAR(255),
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE template_configs IS '模板配置表';
COMMENT ON COLUMN template_configs.模板ID IS '模板唯一标识';
COMMENT ON COLUMN template_configs.模板名称 IS '模板名称（如：职工退休呈报表）';
COMMENT ON COLUMN template_configs.模板类型 IS '模板类型（如：呈报表、审批表、公文）';
COMMENT ON COLUMN template_configs.配置JSON IS '模板配置JSON（包含列宽、行高、单元格样式等）';

-- 2. 字段映射表
CREATE TABLE IF NOT EXISTS template_field_mappings (
    id SERIAL PRIMARY KEY,
    模板ID VARCHAR(50) NOT NULL,
    字段名称 VARCHAR(100) NOT NULL,
    行号 INTEGER NOT NULL,
    列号 INTEGER NOT NULL,
    数据源表 VARCHAR(100),
    数据源字段 VARCHAR(100),
    转换函数 VARCHAR(100),
    默认值 VARCHAR(255),
    UNIQUE(模板ID, 字段名称),
    FOREIGN KEY (模板ID) REFERENCES template_configs(模板ID) ON DELETE CASCADE
);

COMMENT ON TABLE template_field_mappings IS '模板字段映射表';
COMMENT ON COLUMN template_field_mappings.字段名称 IS '字段名称（如：姓名、性别）';
COMMENT ON COLUMN template_field_mappings.行号 IS '单元格所在行号';
COMMENT ON COLUMN template_field_mappings.列号 IS '单元格所在列号';
COMMENT ON COLUMN template_field_mappings.数据源表 IS '数据来源表名';
COMMENT ON COLUMN template_field_mappings.数据源字段 IS '数据来源字段名';
COMMENT ON COLUMN template_field_mappings.转换单数 IS '数据转换函数（如：format_date）';

-- 3. 填报记录表
CREATE TABLE IF NOT EXISTS template_fill_records (
    id SERIAL PRIMARY KEY,
    模板ID VARCHAR(50) NOT NULL,
    填报时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    查询条件 JSONB,
    填报数据 JSONB,
    导出文件路径 VARCHAR(255),
    操作人 VARCHAR(100),
    FOREIGN KEY (模板ID) REFERENCES template_configs(模板ID) ON DELETE CASCADE
);

COMMENT ON TABLE template_fill_records IS '模板填报记录表';
COMMENT ON COLUMN template_fill_records.查询条件 IS '查询条件（如：{"职工ID": "xxx"}）';
COMMENT ON COLUMN template_fill_records.填报数据 IS '填报后的数据JSON';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_template_configs_模板ID ON template_configs(模板ID);
CREATE INDEX IF NOT EXISTS idx_template_field_mappings_模板ID ON template_field_mappings(模板ID);
CREATE INDEX IF NOT EXISTS idx_template_fill_records_模板ID ON template_fill_records(模板ID);
CREATE INDEX IF NOT EXISTS idx_template_fill_records_填报时间 ON template_fill_records(填报时间);
