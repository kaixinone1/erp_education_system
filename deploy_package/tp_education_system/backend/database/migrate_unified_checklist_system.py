"""
统一清单业务系统数据库迁移
整合所有现有的清单/待办功能
"""
import psycopg2
import json
import sys

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def migrate():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("=== 创建统一清单业务系统 ===\n")
        
        # 1. 清单模板主表（业务定义）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_checklist_templates (
                id SERIAL PRIMARY KEY,
                模板编码 VARCHAR(50) UNIQUE NOT NULL,
                模板名称 VARCHAR(100) NOT NULL,
                模板描述 TEXT,
                适用对象类型 VARCHAR(50) DEFAULT '教师', -- 教师、员工、全部
                业务类型 VARCHAR(50), -- 退休、死亡、高龄、合同到期等
                状态 VARCHAR(20) DEFAULT '启用', -- 启用、停用
                触发条件配置 JSONB DEFAULT '[]', -- 触发条件数组
                自动推送 BOOLEAN DEFAULT TRUE, -- 是否自动推送
                创建人 VARCHAR(50),
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建表: business_checklist_templates")
        
        # 2. 清单任务项定义表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_checklist_items (
                id SERIAL PRIMARY KEY,
                模板ID INTEGER REFERENCES business_checklist_templates(id) ON DELETE CASCADE,
                任务序号 INTEGER NOT NULL,
                任务编码 VARCHAR(50),
                任务名称 VARCHAR(100) NOT NULL,
                任务说明 TEXT,
                是否必填 BOOLEAN DEFAULT TRUE,
                办理时限天数 INTEGER, -- NULL表示无时限
                时限计算方式 VARCHAR(20) DEFAULT '清单创建后', -- 清单创建后、触发事件后、前置任务完成后
                提醒方式 VARCHAR(20) DEFAULT '截止前', -- 截止前、当天、逾期后
                提醒提前天数 INTEGER DEFAULT 1,
                关联文档模板ID INTEGER, -- 关联 universal_templates 表
                关联数据表 VARCHAR(100), -- 关联的数据表名
                关联数据字段 JSONB, -- 字段映射配置
                前置任务ID INTEGER REFERENCES business_checklist_items(id) ON DELETE SET NULL,
                允许批量处理 BOOLEAN DEFAULT FALSE,
                排序 INTEGER DEFAULT 0,
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建表: business_checklist_items")
        
        # 3. 清单实例表（推送后的待办）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_checklist_instances (
                id SERIAL PRIMARY KEY,
                模板ID INTEGER REFERENCES business_checklist_templates(id),
                实例编码 VARCHAR(100) UNIQUE, -- 如: RETIRE_2024_001
                关联对象ID INTEGER NOT NULL, -- 教师ID
                关联对象类型 VARCHAR(50) DEFAULT '教师',
                关联对象名称 VARCHAR(100),
                关联对象编码 VARCHAR(50), -- 工号等
                触发事件 JSONB, -- 记录触发详情
                状态 VARCHAR(20) DEFAULT '待处理', -- 待处理、进行中、已完成、已关闭、已逾期
                完成进度 INTEGER DEFAULT 0, -- 0-100
                总任务数 INTEGER DEFAULT 0,
                已完成数 INTEGER DEFAULT 0,
                逾期任务数 INTEGER DEFAULT 0,
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                截止时间 TIMESTAMP, -- 根据时限计算
                实际完成时间 TIMESTAMP,
                处理人 VARCHAR(50),
                备注 TEXT,
                是否归档 BOOLEAN DEFAULT FALSE,
                归档时间 TIMESTAMP
            )
        """)
        print("✓ 创建表: business_checklist_instances")
        
        # 4. 任务处理记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_checklist_item_records (
                id SERIAL PRIMARY KEY,
                实例ID INTEGER REFERENCES business_checklist_instances(id) ON DELETE CASCADE,
                任务项ID INTEGER REFERENCES business_checklist_items(id),
                任务名称 VARCHAR(100),
                完成状态 VARCHAR(20) DEFAULT '未开始', -- 未开始、进行中、已完成、已跳过
                完成时间 TIMESTAMP,
                操作人 VARCHAR(50),
                操作人ID INTEGER,
                处理说明 TEXT,
                附件列表 JSONB DEFAULT '[]',
                关联数据记录ID INTEGER, -- 关联到具体数据表记录
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建表: business_checklist_item_records")
        
        # 5. 触发条件类型定义表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_trigger_type_defs (
                id SERIAL PRIMARY KEY,
                类型编码 VARCHAR(50) UNIQUE NOT NULL,
                类型名称 VARCHAR(100) NOT NULL,
                类型分类 VARCHAR(50), -- 基础信息、时间计算、自定义
                描述 TEXT,
                适用表名 VARCHAR(100), -- 如: teachers
                字段名 VARCHAR(100), -- 如: employment_status
                字段类型 VARCHAR(20), -- string、number、date、boolean
                操作符列表 JSONB DEFAULT '["=", "!=", ">", "<", ">=", "<="]',
                默认值 TEXT,
                是否系统内置 BOOLEAN DEFAULT FALSE,
                是否允许自定义 BOOLEAN DEFAULT TRUE,
                排序 INTEGER DEFAULT 0,
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建表: checklist_trigger_type_defs")
        
        # 6. 插入默认触发条件类型
        cursor.execute("""
            INSERT INTO checklist_trigger_type_defs 
            (类型编码, 类型名称, 类型分类, 描述, 适用表名, 字段名, 字段类型, 操作符列表, 是否系统内置, 排序)
            VALUES 
                ('employment_status', '任职状态', '基础信息', '教师任职状态', 'teachers', 'employment_status', 'string', '["变化为", "=", "!="]', TRUE, 1),
                ('age', '年龄', '时间计算', '根据身份证号计算年龄', 'teachers', 'birth_date', 'number', '[">=", "<=", ">", "<", "="]', TRUE, 2),
                ('work_years', '工龄', '时间计算', '工作年限', 'teachers', 'work_date', 'number', '[">=", "<=", ">", "<", "="]', TRUE, 3),
                ('contract_expire', '合同到期', '时间计算', '合同到期提醒', 'teachers', 'contract_end_date', 'date', '["距离天数<=", "距离天数=", "已过期"]', TRUE, 4),
                ('title_change', '职称变更', '基础信息', '职称发生变化', 'teachers', 'job_title', 'string', '["变化为", "=", "!="]', TRUE, 5),
                ('birthday', '生日提醒', '时间计算', '生日提醒', 'teachers', 'birth_date', 'date', '["距离天数<=", "当天"]', TRUE, 6),
                ('gender', '性别', '基础信息', '性别条件', 'teachers', 'gender', 'string', '["=", "!="]', TRUE, 7),
                ('custom_sql', '自定义SQL', '自定义', '使用自定义SQL条件', NULL, NULL, 'string', '["自定义"]', TRUE, 99)
            ON CONFLICT (类型编码) DO NOTHING
        """)
        print("✓ 插入默认触发条件类型")
        
        # 7. 清单统计视图
        cursor.execute("""
            CREATE OR REPLACE VIEW v_checklist_statistics AS
            SELECT 
                模板ID,
                COUNT(*) as 总实例数,
                SUM(CASE WHEN 状态 = '待处理' THEN 1 ELSE 0 END) as 待处理数,
                SUM(CASE WHEN 状态 = '进行中' THEN 1 ELSE 0 END) as 进行中数,
                SUM(CASE WHEN 状态 = '已完成' THEN 1 ELSE 0 END) as 已完成数,
                SUM(CASE WHEN 状态 = '已逾期' THEN 1 ELSE 0 END) as 已逾期数,
                AVG(完成进度) as 平均进度,
                MAX(创建时间) as 最新创建时间
            FROM business_checklist_instances
            GROUP BY 模板ID
        """)
        print("✓ 创建视图: v_checklist_statistics")
        
        # 8. 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bct_status ON business_checklist_templates(状态)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bct_code ON business_checklist_templates(模板编码)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bci_template ON business_checklist_items(模板ID)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bci_sort ON business_checklist_items(排序)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bci_template_sort ON business_checklist_instances(模板ID, 状态)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bci_object ON business_checklist_instances(关联对象ID, 关联对象类型)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bci_status ON business_checklist_instances(状态)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bcir_instance ON business_checklist_item_records(实例ID)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bcir_item ON business_checklist_item_records(任务项ID)")
        print("✓ 创建索引")
        
        conn.commit()
        print("\n✅ 统一清单业务系统数据库创建完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
