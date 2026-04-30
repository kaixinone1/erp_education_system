#!/usr/bin/env python3
"""
初始化菜单管理系统
创建必要的表：navigation_modules 和 navigation_backups
"""
import psycopg2
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}


def init_database():
    """初始化数据库表"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    print("开始初始化菜单管理系统...")
    
    # 1. 创建导航模块表（扩展版）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS navigation_modules (
            id SERIAL PRIMARY KEY,
            module_id VARCHAR(100) UNIQUE NOT NULL,
            title VARCHAR(200) NOT NULL,
            icon VARCHAR(100),
            path VARCHAR(200),
            type VARCHAR(50) DEFAULT 'module',
            parent_id VARCHAR(100) DEFAULT NULL,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            table_name VARCHAR(100),
            api_endpoint VARCHAR(200),
            component VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] navigation_modules 表已创建/已存在")
    
    # 2. 创建备份表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS navigation_backups (
            id SERIAL PRIMARY KEY,
            backup_name VARCHAR(200),
            modules_data JSONB NOT NULL,
            source VARCHAR(50) DEFAULT 'manual',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100)
        )
    """)
    print("[OK] navigation_backups 表已创建/已存在")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n菜单管理系统初始化完成！")
    print("- navigation_modules: 存储菜单结构（数据库为主）")
    print("- navigation_backups: 存储菜单备份")


if __name__ == "__main__":
    init_database()
