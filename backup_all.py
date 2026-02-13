#!/usr/bin/env python3
"""
全面备份脚本 - 备份数据库和配置文件
"""

import os
import shutil
import json
import subprocess
from datetime import datetime

# 备份目录
BACKUP_DIR = r'd:\erp_thirteen\backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs(BACKUP_DIR, exist_ok=True)

print("=" * 80)
print("开始全面备份")
print("=" * 80)
print(f"备份目录: {BACKUP_DIR}")

# 1. 备份数据库
print("\n1. 备份数据库...")
try:
    db_backup_file = os.path.join(BACKUP_DIR, 'database_backup.sql')
    result = subprocess.run([
        'pg_dump',
        '-h', 'localhost',
        '-U', 'taiping_user',
        '-d', 'taiping_education',
        '-f', db_backup_file
    ], capture_output=True, text=True, env={**os.environ, 'PGPASSWORD': 'taiping_password'})
    
    if result.returncode == 0:
        print(f"   ✓ 数据库备份成功: {db_backup_file}")
    else:
        print(f"   ✗ 数据库备份失败: {result.stderr}")
except Exception as e:
    print(f"   ✗ 数据库备份异常: {e}")

# 2. 备份配置文件
print("\n2. 备份配置文件...")
config_dir = r'd:\erp_thirteen\tp_education_system\backend\config'
config_backup_dir = os.path.join(BACKUP_DIR, 'config')
os.makedirs(config_backup_dir, exist_ok=True)

files_to_backup = [
    'table_name_mappings.json',
    'navigation.json',
    'merged_schema_mappings.json',
    'field_mappings.json',
    'table_schemas.json'
]

for filename in files_to_backup:
    src = os.path.join(config_dir, filename)
    dst = os.path.join(config_backup_dir, filename)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"   ✓ {filename}")
    else:
        print(f"   ✗ {filename} (不存在)")

# 3. 备份字段配置目录
print("\n3. 备份字段配置...")
field_configs_dir = os.path.join(config_dir, 'field_configs')
field_configs_backup_dir = os.path.join(config_backup_dir, 'field_configs')

if os.path.exists(field_configs_dir):
    shutil.copytree(field_configs_dir, field_configs_backup_dir)
    file_count = len([f for f in os.listdir(field_configs_backup_dir) if f.endswith('.json')])
    print(f"   ✓ 字段配置备份成功 ({file_count} 个文件)")
else:
    print(f"   ✗ 字段配置目录不存在")

print("\n" + "=" * 80)
print("备份完成!")
print(f"备份位置: {BACKUP_DIR}")
print("=" * 80)
