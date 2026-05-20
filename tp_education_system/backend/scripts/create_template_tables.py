"""
检查并创建数据库表
"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

try:
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name IN ('template_configs', 'template_field_mappings', 'template_fill_records')
    """)
    
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    if existing_tables:
        print(f"表已存在: {existing_tables}")
        
        for table in existing_tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"已删除表: {table}")
        
        conn.commit()
    
    cursor.execute("""
        CREATE TABLE template_configs (
            id SERIAL PRIMARY KEY,
            模板ID VARCHAR(50) UNIQUE NOT NULL,
            模板名称 VARCHAR(100) NOT NULL,
            模板类型 VARCHAR(50),
            配置JSON JSONB NOT NULL,
            原始文件路径 VARCHAR(255),
            创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("创建表: template_configs")
    
    cursor.execute("""
        CREATE TABLE template_field_mappings (
            id SERIAL PRIMARY KEY,
            模板ID VARCHAR(50) NOT NULL,
            字段名称 VARCHAR(100) NOT NULL,
            行号 INTEGER NOT NULL,
            列号 INTEGER NOT NULL,
            数据源表 VARCHAR(100),
            数据源字段 VARCHAR(100),
            转换函数 VARCHAR(100),
            默认值 VARCHAR(255),
            UNIQUE(模板ID, 字段名称),
            FOREIGN KEY (模板ID) REFERENCES template_configs(模板ID) ON DELETE CASCADE
        )
    """)
    print("创建表: template_field_mappings")
    
    cursor.execute("""
        CREATE TABLE template_fill_records (
            id SERIAL PRIMARY KEY,
            模板ID VARCHAR(50) NOT NULL,
            填报时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            查询条件 JSONB,
            填报数据 JSONB,
            导出文件路径 VARCHAR(255),
            操作人 VARCHAR(100),
            FOREIGN KEY (模板ID) REFERENCES template_configs(模板ID) ON DELETE CASCADE
        )
    """)
    print("创建表: template_fill_records")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_configs_模板ID ON template_configs(模板ID)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_field_mappings_模板ID ON template_field_mappings(模板ID)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_fill_records_模板ID ON template_fill_records(模板ID)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_fill_records_填报时间 ON template_fill_records(填报时间)")
    print("创建索引")
    
    conn.commit()
    
    print("\n数据库表创建成功!")
    print("  1. template_configs - 模板配置表")
    print("  2. template_field_mappings - 字段映射表")
    print("  3. template_fill_records - 填报记录表")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"创建失败: {e}")
    import traceback
    print(traceback.format_exc())
