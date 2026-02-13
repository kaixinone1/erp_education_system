-- 创建退休呈报表中间表
CREATE TABLE IF NOT EXISTS retirement_report_data (
    teacher_id INTEGER PRIMARY KEY REFERENCES teacher_basic_info(id) ON DELETE CASCADE,
    
    -- 基本信息
    name VARCHAR(50),
    gender VARCHAR(10),
    id_card VARCHAR(18),
    birth_date DATE,
    ethnicity VARCHAR(20),
    native_place VARCHAR(100),
    
    -- 档案信息
    archive_birth_date DATE,
    work_start_date DATE,
    archive_work_date DATE,
    
    -- 退休信息
    retirement_date DATE,
    retirement_type VARCHAR(50),
    
    -- 单位信息
    unit_name VARCHAR(200),
    unit_opinion TEXT,
    dept_opinion TEXT,
    approval_date DATE,
    
    -- 计算字段
    work_years INTEGER,
    age INTEGER,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, printed
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_retirement_status ON retirement_report_data(status);

COMMENT ON TABLE retirement_report_data IS '职工退休呈报表中间表';
