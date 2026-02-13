-- 创建一个测试用的中间表：教师培训记录表
CREATE TABLE IF NOT EXISTS teacher_training_records (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES teacher_basic_info(id),
    培训名称 VARCHAR(100),
    培训机构 VARCHAR(100),
    培训开始日期 DATE,
    培训结束日期 DATE,
    培训时长 INTEGER,
    培训证书 VARCHAR(50),
    备注 TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 插入几条测试数据
INSERT INTO teacher_training_records (teacher_id, 培训名称, 培训机构, 培训开始日期, 培训结束日期, 培训时长, 培训证书)
VALUES 
    (273, '2024年暑期教师培训', '市教育局', '2024-07-01', '2024-07-10', 80, '结业证书'),
    (273, '信息技术应用能力提升', '省教育学院', '2024-08-15', '2024-08-20', 40, '合格证书');

-- 查看创建的表结构
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'teacher_training_records' 
ORDER BY ordinal_position;
