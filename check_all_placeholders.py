#!/usr/bin/env python3
"""检查所有占位符的替换情况"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

from services.placeholder_template_engine import PlaceholderTemplateEngine
import psycopg2
import re

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

engine = PlaceholderTemplateEngine(get_db_connection)

template_id = "职工退休申报表html"
teacher_id = 273  # 测试教师ID 273

print("=" * 80)
print(f"检查所有占位符替换情况 - 教师ID: {teacher_id}")
print("=" * 80)

# 获取模板配置
config = engine.get_field_mapping(template_id)
print(f"\n字段映射数量: {len(config['mappings'])}")

# 读取原始模板
template_path = config['file_path']
with open(template_path, 'r', encoding='utf-8') as f:
    original_content = f.read()

# 提取所有占位符
all_placeholders = re.findall(r'\{\{([^{}]+)\}\}', original_content)
all_placeholders = [p.strip() for p in all_placeholders]
unique_placeholders = sorted(list(set(all_placeholders)))

print(f"模板中的唯一占位符: {len(unique_placeholders)} 个")

# 生成文档
html = engine.generate_document(template_id, teacher_id)

# 检查哪些占位符未被替换
remaining = re.findall(r'\{\{([^{}]+)\}\}', html)
remaining = [p.strip() for p in remaining]
remaining_unique = sorted(list(set(remaining)))

print(f"\n未被替换的占位符: {len(remaining_unique)} 个")
for p in remaining_unique:
    # 检查是否有映射
    has_mapping = any(m['placeholder'] == p for m in config['mappings'])
    status = "(已映射但值为空)" if has_mapping else "(未映射)"
    print(f"   - {{{{ {p} }}}} {status}")

print(f"\n已替换的占位符: {len(unique_placeholders) - len(remaining_unique)} 个")

print("\n" + "=" * 80)
