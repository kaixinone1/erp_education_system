#!/usr/bin/env python3
"""创建文档模板表"""
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
    
    # 创建文档模板表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_templates (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            placeholders JSONB DEFAULT '[]',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_templates_type 
        ON document_templates(type)
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("文档模板表创建成功！")

if __name__ == '__main__':
    create_table()
