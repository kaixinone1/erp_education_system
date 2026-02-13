-- 修改 retirement_report_form 表，添加缺失的字段

-- 添加是否独生子女字段
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS is_only_child VARCHAR(10);

-- 添加入党年月字段
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS join_party_date VARCHAR(20);

-- 添加现在住址字段
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS current_address VARCHAR(200);

-- 添加工作简历字段（JSON格式存储多条记录）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS work_experience JSONB DEFAULT '[]'::jsonb;

-- 添加退休原因字段
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS retirement_reason VARCHAR(500);

-- 添加供养直系亲属字段
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS family_members VARCHAR(500);

-- 添加退休后居住地址字段
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS retirement_address VARCHAR(200);

-- 添加发给退休费的单位字段
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS pension_unit VARCHAR(100) DEFAULT '枣阳市人力资源和社会保障局';

-- 添加出生年月字段（用于显示）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS birth_date_display VARCHAR(20);

-- 添加参加工作年月字段（用于显示）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS work_start_date_display VARCHAR(20);

-- 添加工作年限字段（用于显示）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS work_years_display VARCHAR(20);

-- 添加性别字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS gender VARCHAR(10);

-- 添加民族字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS ethnicity VARCHAR(20);

-- 添加文化程度字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS education VARCHAR(50);

-- 添加职务字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS position VARCHAR(50);

-- 添加技术职称字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS title VARCHAR(50);

-- 添加籍贯字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS native_place VARCHAR(100);

-- 添加工作单位字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS work_unit VARCHAR(100);

-- 添加联系电话字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(50);

-- 添加身份证号字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS id_card VARCHAR(20);

-- 添加退休日期字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS retirement_date DATE;

-- 添加年龄字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS age INTEGER;

-- 添加教师姓名字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS teacher_name VARCHAR(50);

-- 添加教师ID字段（确保有）
ALTER TABLE retirement_report_form 
ADD COLUMN IF NOT EXISTS teacher_id INTEGER;
