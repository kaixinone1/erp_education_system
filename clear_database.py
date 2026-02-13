import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 数据库连接信息
conn_info = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

try:
    # 连接到数据库
    print("Connecting to database...")
    conn = psycopg2.connect(**conn_info)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")
    tables = cursor.fetchall()
    
    if not tables:
        print("Database is already empty!")
    else:
        print(f"Found {len(tables)} tables to drop:")
        # 删除所有表
        for table in tables:
            table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        
        # 再次检查是否还有表
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")
        remaining_tables = cursor.fetchall()
        
        if not remaining_tables:
            print("\nDatabase cleared successfully!")
        else:
            print(f"\nWarning: {len(remaining_tables)} tables could not be dropped:")
            for table in remaining_tables:
                print(f"- {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()