#!/usr/bin/env python3
import psycopg2
import json
import os

# 删除数据库表
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 删除表
cursor.execute('DROP TABLE IF EXISTS teacher_education_record CASCADE')
conn.commit()
print('数据库表 teacher_education_record 已删除')

cursor.close()
conn.close()

# 删除映射文件中的记录
config_file = 'd:/erp_thirteen/tp_education_system/backend/config/table_name_mappings.json'

with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 删除教师学历记录的映射
if '教师学历记录' in config.get('mappings', {}):
    del config['mappings']['教师学历记录']
    print('已删除 mappings 中的 教师学历记录')

if 'teacher_education_record' in config.get('reverse_mappings', {}):
    del config['reverse_mappings']['teacher_education_record']
    print('已删除 reverse_mappings 中的 teacher_education_record')

# 保存修改后的配置
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print('配置已更新，现在可以重新导入教师学历记录了')
