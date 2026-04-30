"""
添加清单截止天数字段到业务清单模板表
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
        print("=== 添加清单截止天数字段 ===\n")
        
        # 检查字段是否已存在
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'business_checklist_templates' 
            AND column_name = '清单截止天数'
        """)
        
        if cursor.fetchone():
            print("✓ 字段 '清单截止天数' 已存在")
        else:
            # 添加字段
            cursor.execute("""
                ALTER TABLE business_checklist_templates 
                ADD COLUMN 清单截止天数 INTEGER DEFAULT 30
            """)
            print("✓ 添加字段 '清单截止天数' 成功")
        
        conn.commit()
        print("\n✅ 数据库更新完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
