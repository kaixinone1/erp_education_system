"""
清单模板系统数据库迁移脚本
创建清单模板相关的数据库表
"""
import psycopg2
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
        # 1. 创建清单模板主表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_templates (
                id SERIAL PRIMARY KEY,
                模板名称 VARCHAR(100) NOT NULL,
                模板描述 TEXT,
                适用对象 VARCHAR(50) DEFAULT '教师',
                状态 VARCHAR(20) DEFAULT '启用',
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建表: checklist_templates")
        
        # 2. 创建触发条件表（一个模板可以有多个触发条件）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_trigger_conditions (
                id SERIAL PRIMARY KEY,
                模板ID INTEGER REFERENCES checklist_templates(id) ON DELETE CASCADE,
                条件名称 VARCHAR(100),
                条件类型 VARCHAR(50) NOT NULL, -- '状态变更', '年龄', '工龄', '合同到期', '职称变更', '自定义'
                条件字段 VARCHAR(100), -- 数据库字段名或自定义字段
                操作符 VARCHAR(20), -- '=', '!=', '>', '<', '>=', '<=', '包含', '距离天数<=', '变化为'
                条件值 TEXT, -- 目标值
                自定义条件SQL TEXT, -- 高级用户可以直接写条件SQL
                排序 INTEGER DEFAULT 0,
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建表: checklist_trigger_conditions")
        
        # 3. 创建清单任务项定义表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_template_items (
                id SERIAL PRIMARY KEY,
                模板ID INTEGER REFERENCES checklist_templates(id) ON DELETE CASCADE,
                任务序号 INTEGER NOT NULL,
                任务名称 VARCHAR(100) NOT NULL,
                任务说明 TEXT,
                是否必填 BOOLEAN DEFAULT TRUE,
                关联文档模板ID INTEGER, -- 关联 universal_templates 表
                前置任务ID INTEGER REFERENCES checklist_template_items(id) ON DELETE SET NULL,
                办理时限天数 INTEGER, -- 如：3表示3天内完成，NULL表示无时限
                时限提醒方式 VARCHAR(20) DEFAULT '截止前', -- '截止前', '当天', '逾期后'
                排序 INTEGER DEFAULT 0,
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建表: checklist_template_items")
        
        # 4. 创建待办工作实例表（推送后的清单实例）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_instances (
                id SERIAL PRIMARY KEY,
                模板ID INTEGER REFERENCES checklist_templates(id),
                关联对象ID INTEGER NOT NULL, -- 教师ID等
                关联对象类型 VARCHAR(50) DEFAULT '教师',
                关联对象名称 VARCHAR(100),
                触发条件详情 JSONB, -- 记录触发时的条件详情
                状态 VARCHAR(20) DEFAULT '待处理', -- '待处理', '进行中', '已完成', '已关闭'
                完成进度 INTEGER DEFAULT 0, -- 0-100
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                截止时间 TIMESTAMP, -- 根据办理时限计算
                完成时间 TIMESTAMP,
                备注 TEXT
            )
        """)
        print("✓ 创建表: checklist_instances")
        
        # 5. 创建任务处理记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_item_records (
                id SERIAL PRIMARY KEY,
                实例ID INTEGER REFERENCES checklist_instances(id) ON DELETE CASCADE,
                任务项ID INTEGER REFERENCES checklist_template_items(id),
                完成状态 BOOLEAN DEFAULT FALSE,
                完成时间 TIMESTAMP,
                操作人 VARCHAR(50),
                备注 TEXT,
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建表: checklist_item_records")
        
        # 6. 创建触发条件类型枚举数据
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_trigger_types (
                id SERIAL PRIMARY KEY,
                类型编码 VARCHAR(50) UNIQUE NOT NULL,
                类型名称 VARCHAR(100) NOT NULL,
                描述 TEXT,
                默认字段 VARCHAR(100),
                可用操作符 JSONB, -- ['=', '!=', '>', '<', '变化为']
                是否系统内置 BOOLEAN DEFAULT FALSE,
                排序 INTEGER DEFAULT 0
            )
        """)
        
        # 插入默认触发条件类型
        cursor.execute("""
            INSERT INTO checklist_trigger_types (类型编码, 类型名称, 描述, 默认字段, 可用操作符, 是否系统内置, 排序)
            VALUES 
                ('status_change', '任职状态变更', '当教师任职状态发生变化时触发', 'employment_status', '["变化为", "!=", "="]', TRUE, 1),
                ('age', '年龄条件', '当年龄满足条件时触发', '年龄', '[">=", "<=", ">", "<", "="]', TRUE, 2),
                ('work_years', '工龄条件', '当工龄满足条件时触发', 'work_years', '[">=", "<=", ">", "<", "="]', TRUE, 3),
                ('contract_expire', '合同到期', '当合同即将到期时触发', '合同到期日', '["距离天数<=", "距离天数=", "已过期"]', TRUE, 4),
                ('title_change', '职称变更', '当职称发生变化时触发', 'job_title', '["变化为", "!=", "="]', TRUE, 5),
                ('birthday', '生日提醒', '当到达生日时触发', 'birth_date', '["距离天数<=", "当天"]', TRUE, 6),
                ('custom', '自定义条件', '使用自定义SQL或字段', NULL, '["=", "!=", ">", "<", ">=", "<=", "包含", "正则匹配"]', FALSE, 99)
            ON CONFLICT (类型编码) DO NOTHING
        """)
        print("✓ 插入默认触发条件类型")
        
        # 7. 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checklist_templates_status ON checklist_templates(状态)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trigger_conditions_template_id ON checklist_trigger_conditions(模板ID)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_items_template_id ON checklist_template_items(模板ID)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_instances_status ON checklist_instances(状态)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_instances_object ON checklist_instances(关联对象ID, 关联对象类型)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_records_instance ON checklist_item_records(实例ID)")
        print("✓ 创建索引")
        
        conn.commit()
        print("\n✅ 清单模板系统数据库迁移完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
