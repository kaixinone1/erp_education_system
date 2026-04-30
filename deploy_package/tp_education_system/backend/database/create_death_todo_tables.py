"""
创建教师死亡待办工作业务清单相关表
"""
import psycopg2
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_tables():
    """创建教师死亡待办工作相关表"""
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )
    cursor = conn.cursor()

    try:
        # 1. 创建教师死亡待办工作主表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS 教师死亡待办工作 (
                id SERIAL PRIMARY KEY,
                教师ID INTEGER NOT NULL,
                教师姓名 VARCHAR(100),
                身份证号码 VARCHAR(18),
                死亡日期 DATE,
                状态 VARCHAR(50) DEFAULT '待处理',
                完成进度 INTEGER DEFAULT 0,
                创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                完成时间 TIMESTAMP,
                更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                备注 TEXT
            )
        """)
        print("✓ 创建表: 教师死亡待办工作")

        # 2. 创建教师死亡待办工作处理记录表（存储10个任务的完成情况）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS 教师死亡待办处理记录 (
                id SERIAL PRIMARY KEY,
                待办ID INTEGER NOT NULL REFERENCES 教师死亡待办工作(id) ON DELETE CASCADE,
                任务1_收集死亡证明 BOOLEAN DEFAULT FALSE,
                任务2_打印终保承诺书 BOOLEAN DEFAULT FALSE,
                任务3_扫描上传材料 BOOLEAN DEFAULT FALSE,
                任务4_填报抚恤金审批表 BOOLEAN DEFAULT FALSE,
                任务5_送审材料 BOOLEAN DEFAULT FALSE,
                任务6_机关中心签批 BOOLEAN DEFAULT FALSE,
                任务7_工资科预审核 BOOLEAN DEFAULT FALSE,
                任务8_教育局审批 BOOLEAN DEFAULT FALSE,
                任务9_人社局审批 BOOLEAN DEFAULT FALSE,
                任务10_财政局备案 BOOLEAN DEFAULT FALSE,
                完成进度 INTEGER DEFAULT 0,
                操作人 VARCHAR(100),
                操作时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建表: 教师死亡待办处理记录")

        # 3. 创建死亡登记信息表（用于80周岁高龄管理死亡登记）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS 死亡登记信息 (
                id SERIAL PRIMARY KEY,
                教师ID INTEGER,
                教师姓名 VARCHAR(100),
                身份证号码 VARCHAR(18),
                死亡日期 DATE NOT NULL,
                死亡原因 VARCHAR(200),
                登记时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                登记人 VARCHAR(100),
                备注 TEXT
            )
        """)
        print("✓ 创建表: 死亡登记信息")

        # 4. 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_death_todo_teacher_id 
            ON 教师死亡待办工作(教师ID)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_death_todo_status 
            ON 教师死亡待办工作(状态)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_death_process_todo_id 
            ON 教师死亡待办处理记录(待办ID)
        """)
        print("✓ 创建索引")

        conn.commit()
        print("\n所有表创建成功！")

    except Exception as e:
        conn.rollback()
        print(f"创建表失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_tables()
