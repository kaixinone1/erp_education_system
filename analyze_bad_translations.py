import json
import re

# 读取分析结果
with open('d:\\erp_thirteen\\translation_analysis.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

# 提取需要改进的字段名
bad_translations = analysis['bad_translations']

# 手动定义需要改进的字段名的新翻译
manual_translations = {
    '证书资格种类': 'certificate_type',
    '学段学科': 'education_stage_subject',
    '学科': 'subject',
    '发证机关': 'issuing_authority',
    '级别薪级': 'salary_level',
    '学段': 'education_stage',
    '是否已评未聘': 'is_evaluated_not_appointed',
    '批准文号': 'approval_document_number',
    '是否占岗': 'is_occupying_post',
    '金额': 'amount',
}

# 过滤掉临时文件名和Unnamed列
real_bad_translations = []
for item in bad_translations:
    chinese = item['chinese']
    # 跳过临时文件名
    if chinese.startswith('tmp') or chinese.startswith('Unnamed:') or re.match(r'\d{4}-\d{2}-\d{2}', chinese):
        continue
    # 跳过已经是英文的
    if re.match(r'^[a-zA-Z_]+$', chinese):
        continue
    real_bad_translations.append(item)

print("=" * 80)
print("需要重新翻译的字段名")
print("=" * 80)

print(f"\n总共需要重新翻译：{len(real_bad_translations)} 个字段")

print("\n字段名列表：")
for item in real_bad_translations:
    chinese = item['chinese']
    english = item['english']
    new_english = manual_translations.get(chinese, '待定')
    print(f"  {chinese:30s} -> {english:30s} | 建议：{new_english}")

# 保存需要重新翻译的字段名
with open('d:\\erp_thirteen\\need_retranslate_fields.json', 'w', encoding='utf-8') as f:
    json.dump(real_bad_translations, f, ensure_ascii=False, indent=2)

print(f"\n已保存到：d:\\erp_thirteen\\need_retranslate_fields.json")
