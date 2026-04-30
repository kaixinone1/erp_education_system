"""
迁移脚本：在教师死亡待办处理记录表中增加第11项任务
任务11：在绩效工资审批表中处理绩效，标明死亡信息
"""
import psycopg2

def migrate():
    """添加第11项任务字段"""
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )
    cursor = conn.cursor()

    try:
        # 检查字段是否已存在
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '教师死亡待办处理记录' 
            AND column_name = '任务11_处理绩效工资'
        """)
        
        if cursor.fetchone():
            print("字段 任务11_处理绩效工资 已存在，跳过迁移")
        else:
            # 添加第11项任务字段
            cursor.execute("""
                ALTER TABLE 教师死亡待办处理记录 
                ADD COLUMN 任务11_处理绩效工资 BOOLEAN DEFAULT FALSE
            """)
            print("✓ 添加字段: 任务11_处理绩效工资")
        
        conn.commit()
        print("\n迁移完成！")

    except Exception as e:
        conn.rollback()
        print(f"迁移失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    migrate()
