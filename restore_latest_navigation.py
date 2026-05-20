import json
import shutil

# 恢复刚才备份的菜单
current_file = 'd:/erp_thirteen/tp_education_system/backend/config/navigation.json'
backup_file = 'd:/erp_thirteen/tp_education_system/backend/config/navigation_backup_20260507_101013.json'

shutil.copy(backup_file, current_file)
print(f"已恢复菜单到: {backup_file}")

print("\n菜单已恢复！")
