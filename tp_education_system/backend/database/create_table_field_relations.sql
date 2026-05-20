-- 表字段关联关系缓存表
-- 用于缓存表间关联关系和字典值，提升查询性能

CREATE TABLE IF NOT EXISTS table_field_relations (
    id SERIAL PRIMARY KEY,
    
    -- 表信息
    table_name VARCHAR(255) NOT NULL,           -- 英文表名
    表名 VARCHAR(255),                          -- 中文表名
    
    -- 字段信息
    field_name VARCHAR(255) NOT NULL,           -- 英文字段名
    字段名 VARCHAR(255),                        -- 中文字段名
    数据类型 VARCHAR(100),                      -- 字段数据类型
    
    -- 关联信息
    关联类型 VARCHAR(50),                       -- 关联类型：to_master, to_dict, none
    关联表 VARCHAR(255),                        -- 关联的表名
    关联字段 VARCHAR(255),                      -- 关联的字段名
    关联显示字段 VARCHAR(255),                  -- 关联显示字段
    
    -- 字典值缓存（JSON格式）
    字典值列表 JSON,                            -- 字典值列表 [{"值": "xxx", "标签": "xxx"}]
    字典值数量 INTEGER DEFAULT 0,               -- 字典值数量
    
    -- 元数据
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束
    UNIQUE(table_name, field_name)
);

-- 创建索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_table_name ON table_field_relations(table_name);
CREATE INDEX IF NOT EXISTS idx_关联类型 ON table_field_relations(关联类型);
CREATE INDEX IF NOT EXISTS idx_关联表 ON table_field_relations(关联表);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.更新时间 = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_table_field_relations_updated_at 
    BEFORE UPDATE ON table_field_relations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 添加表注释
COMMENT ON TABLE table_field_relations IS '表字段关联关系缓存表 - 用于缓存表间关联关系和字典值';
COMMENT ON COLUMN table_field_relations.table_name IS '英文表名';
COMMENT ON COLUMN table_field_relations.表名 IS '中文表名';
COMMENT ON COLUMN table_field_relations.field_name IS '英文字段名';
COMMENT ON COLUMN table_field_relations.字段名 IS '中文字段名';
COMMENT ON COLUMN table_field_relations.关联类型 IS '关联类型：to_master-主表关联, to_dict-字典关联, none-无关联';
COMMENT ON COLUMN table_field_relations.字典值列表 IS '字典值列表，JSON格式';
COMMENT ON COLUMN table_field_relations.字典值数量 IS '字典值数量，用于前端智能选择菜单类型';
