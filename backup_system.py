#!/usr/bin/env python3
"""
系统全面备份脚本
"""

import os
import shutil
import subprocess
from datetime import datetime

def backup_database():
    """备份PostgreSQL数据库"""
    print("=" * 80)
    print("1. 备份数据库")
    print("=" * 80)
    
    backup_dir = r'd:\erp_thirteen\backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'{backup_dir}\db_backup_{timestamp}.sql'
    
    # 使用pg_dump备份
    cmd = [
        'pg_dump',
        '-h', 'localhost',
        '-U', 'taiping_user',
        '-d', 'taiping_education',
        '-f', backup_file
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = 'taiping_password'
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ 数据库备份成功: {backup_file}")
            return True
        else:
            print(f"  ✗ 数据库备份失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ 数据库备份异常: {e}")
        return False

def backup_code():
    """备份代码文件"""
    print("\n" + "=" * 80)
    print("2. 备份代码文件")
    print("=" * 80)
    
    source_dirs = [
        (r'd:\erp_thirteen\tp_education_system\backend', 'backend'),
        (r'd:\erp_thirteen\tp_education_system\frontend\src', 'frontend_src'),
    ]
    
    backup_dir = r'd:\erp_thirteen\backups'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for source, name in source_dirs:
        backup_path = f'{backup_dir}\{name}_{timestamp}'
        try:
            shutil.copytree(source, backup_path, ignore=shutil.ignore_patterns('__pycache__', 'node_modules', '.git'))
            print(f"  ✓ {name} 备份成功: {backup_path}")
        except Exception as e:
            print(f"  ✗ {name} 备份失败: {e}")

def backup_configs():
    """备份配置文件"""
    print("\n" + "=" * 80)
    print("3. 备份配置文件")
    print("=" * 80)
    
    config_files = [
        r'd:\erp_thirteen\tp_education_system\backend\config\import_config.json',
        r'd:\erp_thirteen\tp_education_system\backend\config\table_schemas.json',
        r'd:\erp_thirteen\tp_education_system\backend\config\merged_schema_mappings.json',
    ]
    
    backup_dir = r'd:\erp_thirteen\backups\configs'
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for config_file in config_files:
        if os.path.exists(config_file):
            filename = os.path.basename(config_file)
            backup_path = f'{backup_dir}\{filename}_{timestamp}'
            try:
                shutil.copy2(config_file, backup_path)
                print(f"  ✓ {filename} 备份成功")
            except Exception as e:
                print(f"  ✗ {filename} 备份失败: {e}")
        else:
            print(f"  ⚠ {config_file} 不存在")

def list_tables():
    """列出所有表"""
    print("\n" + "=" * 80)
    print("4. 列出数据库中的所有表")
    print("=" * 80)
    
    import psycopg2
    
    DB_PARAMS = {
        'host': 'localhost',
        'database': 'taiping_education',
        'user': 'taiping_user',
        'password': 'taiping_password'
    }
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        # 保存表列表
        backup_dir = r'd:\erp_thirteen\backups'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        list_file = f'{backup_dir}\tables_list_{timestamp}.txt'
        
        with open(list_file, 'w', encoding='utf-8') as f:
            f.write(f"数据库表列表 ({timestamp})\n")
            f.write("=" * 80 + "\n\n")
            for table in tables:
                f.write(f"{table}\n")
        
        print(f"  ✓ 表列表已保存: {list_file}")
        print(f"  共 {len(tables)} 个表")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"  ✗ 获取表列表失败: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("开始系统全面备份")
    print("=" * 80)
    
    backup_database()
    backup_code()
    backup_configs()
    list_tables()
    
    print("\n" + "=" * 80)
    print("备份完成！")
    print("=" * 80)
    print(f"备份目录: d:\erp_thirteen\backups")
