"""
创建表字段关联关系缓存表
"""
import psycopg2
import os

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def create_table():
    sql_file = os.path.join(os.path.dirname(__file__), 'database', 'create_table_field_relations.sql')
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        cursor.execute(sql)
        conn.commit()
        
        print("[OK] 表字段关联关系缓存表创建成功")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[错误] 创建表失败: {e}")
        raise

if __name__ == "__main__":
    create_table()
