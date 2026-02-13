#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 删除旧表（如果存在）
cursor.execute("DROP TABLE IF EXISTS retirement_report_data")

# 创建新的退休呈报表中间表
cursor.execute("""
CREATE TABLE retirement_report_data (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES teacher_basic_info(id) ON DELETE CASCADE,
    
    -- 基本信息
    id_card VARCHAR(18),
    position VARCHAR(100),
    name VARCHAR(50),
    gender VARCHAR(10),
    birth_date DATE,
    ethnicity VARCHAR(20),
    education VARCHAR(50),
    is_only_child BOOLEAN DEFAULT FALSE,
    party_join_date DATE,
    job_title VARCHAR(100),
    tech_title VARCHAR(100),
    work_start_date DATE,
    work_years INTEGER,
    native_place VARCHAR(100),
    current_address VARCHAR(200),
    
    -- 退休信息
    retirement_reason VARCHAR(200),
    retirement_address VARCHAR(200),
    retirement_date DATE,
    
    -- 2014年9月30日岗位信息
    post_20140930_specialty VARCHAR(100),
    post_20140930_specialty_level VARCHAR(50),
    post_20140930_specialty_salary INTEGER,
    post_20140930_worker VARCHAR(100),
    post_20140930_worker_level VARCHAR(50),
    post_20140930_worker_salary INTEGER,
    
    -- 最后一次职务升降
    last_promotion_date DATE,
    last_position VARCHAR(100),
    last_position_level VARCHAR(50),
    last_position_salary INTEGER,
    last_worker VARCHAR(100),
    last_worker_level VARCHAR(50),
    last_worker_salary INTEGER,
    
    -- 退休时岗位
    retirement_specialty VARCHAR(100),
    retirement_specialty_level VARCHAR(50),
    retirement_specialty_salary INTEGER,
    retirement_worker VARCHAR(100),
    retirement_worker_level VARCHAR(50),
    retirement_worker_salary INTEGER,
    
    -- 工作经历
    work_history TEXT,
    
    -- 直系亲属供养情况
    family_support TEXT,
    
    -- 单位意见
    unit_opinion TEXT,
    dept_opinion TEXT,
    approval_date DATE,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 创建索引
cursor.execute("CREATE INDEX idx_retirement_report_teacher ON retirement_report_data(teacher_id)")
cursor.execute("CREATE INDEX idx_retirement_report_status ON retirement_report_data(status)")

conn.commit()
cursor.close()
conn.close()

print('退休呈报表中间表创建成功！')
print('包含字段：身份证号码、岗位、姓名、性别、出生日期、民族、文化程度、是否独生子女、')
print('入党年月、职务、技术职称、参加工作时间、工作年限、籍贯、现住址、退休原因、')
print('退休后居住地址、退休时间、2014年9月30日岗位信息、最后一次职务升降、')
print('退休时岗位、工作经历、直系亲属供养情况等')
