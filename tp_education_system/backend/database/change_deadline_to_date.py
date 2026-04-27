"""
将清单截止天数修改为截止日期
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
        print("=== 修改清单截止天数字段为截止日期 ===\n")
        
        # 检查字段是否存在
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'business_checklist_templates' 
            AND column_name = '清单截止天数'
        """)
        
        if cursor.fetchone():
            # 先删除旧字段
            cursor.execute("""
                ALTER TABLE business_checklist_templates 
                DROP COLUMN 清单截止天数
            """)
            print("✓ 删除旧字段 '清单截止天数'")
            
            # 添加新字段
            cursor.execute("""
                ALTER TABLE business_checklist_templates 
                ADD COLUMN 截止日期 DATE
            """)
            print("✓ 添加新字段 '截止日期' (DATE类型)")
        else:
            # 检查截止日期字段是否已存在
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'business_checklist_templates' 
                AND column_name = '截止日期'
            """)
            
            if not cursor.fetchone():
                # 添加新字段
                cursor.execute("""
                    ALTER TABLE business_checklist_templates 
                    ADD COLUMN 截止日期 DATE
                """)
                print("✓ 添加字段 '截止日期'")
        
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
