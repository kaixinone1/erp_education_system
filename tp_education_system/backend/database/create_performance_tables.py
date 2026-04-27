"""
创建绩效工资审批表相关的数据库表
"""
import psycopg2
from datetime import datetime

def create_performance_tables():
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )
    cursor = conn.cursor()

    # 1. 人员变动记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel_change_records (
            id SERIAL PRIMARY KEY,
            teacher_id INTEGER REFERENCES teacher_basic_info(id),
            change_type VARCHAR(50) NOT NULL,  -- 退休、调离、调出、离职、辞职、去世、晋升
            previous_status VARCHAR(50),
            new_status VARCHAR(50),
            change_date DATE,  -- 实际发生日期
            effective_month VARCHAR(7),  -- 正式生效月份 YYYY-MM
            cancel_performance_month VARCHAR(7),  -- 取消绩效月份 YYYY-MM
            stop_salary_month VARCHAR(7),  -- 停发工资月份
            stop_social_security_month VARCHAR(7),  -- 社保暂停月份
            stop_medical_insurance_month VARCHAR(7),  -- 医保暂停月份
            annual_assessment_unit BOOLEAN,  -- 年度考核是否在本单位
            transfer_salary_relation BOOLEAN,  -- 是否转出工资关系
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ 人员变动记录表创建成功")

    # 2. 岗位设置遗留问题表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS position_legacy_issues (
            id SERIAL PRIMARY KEY,
            teacher_id INTEGER REFERENCES teacher_basic_info(id),
            amount DECIMAL(10,2),  -- 金额
            remarks TEXT,
            effective_month VARCHAR(7),  -- 生效月份 YYYY-MM
            expiry_month VARCHAR(7),  -- 失效月份 YYYY-MM
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ 岗位设置遗留问题表创建成功")

    # 3. 绩效审批表主表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_pay_approval (
            id SERIAL PRIMARY KEY,
            year_month VARCHAR(7) NOT NULL UNIQUE,  -- 年月 YYYY-MM
            report_unit VARCHAR(100) DEFAULT '太平中心学校',
            report_date DATE,
            total_people INTEGER DEFAULT 0,  -- 绩效人数
            total_amount DECIMAL(12,2) DEFAULT 0,  -- 绩效工资合计
            town_subsidy_people INTEGER DEFAULT 0,  -- 乡镇补贴人数
            town_subsidy_standard DECIMAL(10,2) DEFAULT 350,  -- 乡镇补贴标准
            town_subsidy_amount DECIMAL(12,2) DEFAULT 0,  -- 乡镇补贴金额
            retired_cadre_count INTEGER DEFAULT 0,  -- 退休干部人数
            retired_worker_count INTEGER DEFAULT 0,  -- 退休工人人数
            retired_cadre_office_count INTEGER DEFAULT 0,  -- 离休干部人数
            legacy_total_amount DECIMAL(10,2) DEFAULT 0,  -- 岗位设置遗留问题合计
            legacy_total_people INTEGER DEFAULT 0,  -- 岗位设置遗留问题人数
            remarks TEXT,  -- 备注（自动生成）
            status VARCHAR(20) DEFAULT 'draft',  -- draft, generated, exported, uploaded
            excel_file_path VARCHAR(500),
            pdf_file_path VARCHAR(500),
            scanned_file_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ 绩效审批表主表创建成功")

    # 4. 绩效审批表明细表（各岗位人数和金额）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_pay_approval_detail (
            id SERIAL PRIMARY KEY,
            approval_id INTEGER REFERENCES performance_pay_approval(id),
            category VARCHAR(50) NOT NULL,  -- 类别：行政管理人员、专业技术人员、工人
            level_name VARCHAR(50) NOT NULL,  -- 级别名称
            people_count INTEGER DEFAULT 0,  -- 人数
            monthly_standard DECIMAL(10,2) DEFAULT 0,  -- 月工资标准
            subtotal DECIMAL(12,2) DEFAULT 0,  -- 小计
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ 绩效审批表明细表创建成功")

    # 5. 绩效工资标准字典表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_pay_standards (
            id SERIAL PRIMARY KEY,
            category VARCHAR(50) NOT NULL,  -- 类别：行政管理人员、专业技术人员、工人
            level_name VARCHAR(50) NOT NULL,  -- 级别名称
            monthly_standard DECIMAL(10,2) NOT NULL,  -- 月工资标准
            effective_date DATE,  -- 生效日期
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category, level_name)
        )
    """)
    print("✓ 绩效工资标准字典表创建成功")

    # 6. 乡镇补贴标准字典表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS town_subsidy_standards (
            id SERIAL PRIMARY KEY,
            standard_amount DECIMAL(10,2) DEFAULT 350,  -- 标准金额
            effective_date DATE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ 乡镇补贴标准字典表创建成功")

    conn.commit()
    cursor.close()
    conn.close()
    print("\n所有表创建完成！")

if __name__ == "__main__":
    create_performance_tables()
