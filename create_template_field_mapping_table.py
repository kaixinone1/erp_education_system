#!/usr/bin/env python3
"""创建模板字段映射表"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def create_table():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 创建模板字段映射表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS template_field_mapping (
            id SERIAL PRIMARY KEY,
            template_id INTEGER NOT NULL,
            template_name VARCHAR(200),
            placeholder_name VARCHAR(100) NOT NULL,
            intermediate_table VARCHAR(100) NOT NULL,
            intermediate_table_cn VARCHAR(200),
            intermediate_field VARCHAR(100) NOT NULL,
            intermediate_field_cn VARCHAR(200),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(template_id, placeholder_name)
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_template_field_mapping_template_id 
        ON template_field_mapping(template_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_template_field_mapping_intermediate_table 
        ON template_field_mapping(intermediate_table)
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("模板字段映射表创建成功！")

if __name__ == '__main__':
    create_table()
