#!/usr/bin/env python3
"""修复字段映射配置 - 使占位符和数据库字段名匹配"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 获取模板ID
cursor.execute("SELECT id FROM document_templates WHERE template_id = %s", ('职工退休申报表html',))
template_row = cursor.fetchone()
template_id = template_row[0]

print("修复字段映射配置...")
print("=" * 60)

# 需要修复的映射：占位符 -> 正确的数据库字段名
fixes = [
    # 岗位和职务映射修正
    ('岗位1', '事业管理岗位1'),
    ('职务1', '对应原职务1'),
    ('岗位2', '事业专技岗位2'),
    ('职务2', '对应原职务2'),
    ('岗位3', '事业工勤岗位3'),
    ('职务3', '对应技术等级3'),
    ('岗位4', '事业管理岗位4'),
    ('职务4', '对应原职务4'),
    ('岗位5', '事业专技岗位5'),
    ('职务5', '对应原职务5'),
    ('岗位6', '事业工勤岗位6'),
    ('职务6', '对应技术等级6'),
    ('岗位7', '退休时事业管理岗位7'),
    ('职务7', '对应原职务7'),
    ('岗位8', '退休时事业专技岗位8'),
    ('职务8', '对应原职务8'),
    ('岗位9', '退休时事业工勤岗位9'),
    ('职务9', '对应技术等级9'),
    
    # 其他字段修正
    ('在何单位任何职', '所在单位及职务'),
    ('证明人及其住址', '证明人及其住址'),  # 这个应该正确
    ('直系亲属信息', '直系亲属信息'),  # 这个应该正确
]

for placeholder, correct_field in fixes:
    # 检查当前映射
    cursor.execute("""
        SELECT id, intermediate_field FROM template_field_mapping 
        WHERE template_id = %s AND placeholder_name = %s
    """, (template_id, placeholder))
    
    row = cursor.fetchone()
    if row:
        mapping_id, current_field = row
        if current_field != correct_field:
            # 更新映射
            cursor.execute("""
                UPDATE template_field_mapping 
                SET intermediate_field = %s, updated_at = NOW()
                WHERE id = %s
            """, (correct_field, mapping_id))
            print(f"  更新: {{{{ {placeholder} }}}} -> {correct_field} (原: {current_field})")
        else:
            print(f"  正确: {{{{ {placeholder} }}}} -> {correct_field}")
    else:
        # 添加新映射
        cursor.execute("""
            INSERT INTO template_field_mapping 
            (template_id, placeholder_name, intermediate_table, intermediate_field, is_active, created_at, updated_at)
            VALUES (%s, %s, 'retirement_report_data', %s, true, NOW(), NOW())
        """, (template_id, placeholder, correct_field))
        print(f"  添加: {{{{ {placeholder} }}}} -> {correct_field}")

conn.commit()
print("\n" + "=" * 60)
print("修复完成!")

cursor.close()
conn.close()
