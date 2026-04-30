-- 创建模板页面设置表
CREATE TABLE IF NOT EXISTS template_page_settings (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(255) NOT NULL,
    
    -- 通用页面设置
    paper_size VARCHAR(20),       -- A3/A4/A5/Letter
    orientation VARCHAR(20),      -- portrait(纵向)/landscape(横向)
    width_cm NUMERIC(10, 2),      -- 页面宽度
    height_cm NUMERIC(10, 2),     -- 页面高度
    margin_left_cm NUMERIC(10, 2),
    margin_right_cm NUMERIC(10, 2),
    margin_top_cm NUMERIC(10, 2),
    margin_bottom_cm NUMERIC(10, 2),
    
    -- Word特有
    word_tables JSONB,            -- 表格结构信息
    
    -- Excel特有  
    excel_sheets JSONB,           -- 工作表信息
    
    -- PDF特有
    pdf_pages JSONB,              -- 页面信息
    
    -- HTML特有
    html_structure JSONB,         -- HTML结构
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(template_id)
);

-- 添加注释
COMMENT ON TABLE template_page_settings IS '模板页面设置表，存储各种格式模板的页面设置信息';
COMMENT ON COLUMN template_page_settings.paper_size IS '纸张大小：A3/A4/A5/Letter';
COMMENT ON COLUMN template_page_settings.orientation IS '纸张方向：portrait(纵向)/landscape(横向)';

-- 创建占位符位置表
CREATE TABLE IF NOT EXISTS template_placeholders (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(255) NOT NULL,
    placeholder_name VARCHAR(100) NOT NULL,    -- 如：{{姓名}}
    
    -- 格式类型
    format_type VARCHAR(20),          -- word/excel/pdf/html
    
    -- Word/Excel：表格位置
    table_index INTEGER,
    row_index INTEGER,
    cell_index INTEGER,
    
    -- PDF：坐标位置
    page_num INTEGER,
    x_pos NUMERIC(10, 2),
    y_pos NUMERIC(10, 2),
    
    -- HTML：CSS选择器
    css_selector TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(template_id, placeholder_name)
);

-- 添加注释
COMMENT ON TABLE template_placeholders IS '模板占位符位置表，存储占位符在模板中的精确位置';
COMMENT ON COLUMN template_placeholders.placeholder_name IS '占位符名称，如：{{姓名}}';
COMMENT ON COLUMN template_placeholders.format_type IS '格式类型：word/excel/pdf/html';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_template_placeholders_template_id ON template_placeholders(template_id);
CREATE INDEX IF NOT EXISTS idx_template_placeholders_name ON template_placeholders(placeholder_name);
