import re

# 读取文件
file_path = r'd:\erp_thirteen\tp_education_system\backend\routes\template_field_mapping_routes.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复所有 int(template_id) 的地方
# 模式1: try: template_id_int = int(template_id) except ValueError: ...
content = re.sub(
    r'try:\s*\n\s*try:\s*\n\s*template_id_int = int\(template_id\)\s*\n\s*except ValueError:\s*\n\s*raise HTTPException\(status_code=400, detail=f"无效的模板ID: \{template_id\}"\)',
    '# 支持字符串类型的模板ID\n        template_id_str = template_id',
    content
)

# 模式2: 单独替换 template_id_int 为 template_id_str
content = content.replace('template_id_int)', 'template_id_str)')
content = content.replace('template_id_int,', 'template_id_str,')

# 保存文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('修复完成')

# 检查是否还有剩余
if 'int(template_id)' in content:
    print('警告：还有未修复的 int(template_id)')
    # 找出位置
    for i, line in enumerate(content.split('\n')):
        if 'int(template_id)' in line:
            print(f'  行 {i+1}: {line.strip()}')
else:
    print('所有 int(template_id) 已修复')
