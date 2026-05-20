import json

# 读取配置文件
with open('d:/erp_thirteen/tp_education_system/backend/config/table_name_mappings.json', 'r', encoding='utf-8') as f:
    mappings = json.load(f)

# 更新"岗位聘任信息"的英文表名
if "岗位聘任信息" in mappings["mappings"]:
    old_name = mappings["mappings"]["岗位聘任信息"]["english_name"]
    mappings["mappings"]["岗位聘任信息"]["english_name"] = "post_appointment_info"
    
    # 更新反向映射
    if old_name in mappings["reverse_mappings"]:
        del mappings["reverse_mappings"][old_name]
    mappings["reverse_mappings"]["post_appointment_info"] = "岗位聘任信息"
    
    print(f"已更新：岗位聘任信息")
    print(f"  旧表名: {old_name}")
    print(f"  新表名: post_appointment_info")

# 保存配置文件
with open('d:/erp_thirteen/tp_education_system/backend/config/table_name_mappings.json', 'w', encoding='utf-8') as f:
    json.dump(mappings, f, ensure_ascii=False, indent=2)

print("\n配置文件已更新！")
