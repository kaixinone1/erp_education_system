import json
import shutil
from datetime import datetime

# 备份当前菜单（以防万一）
current_file = 'd:/erp_thirteen/tp_education_system/backend/config/navigation.json'
backup_file = f'd:/erp_thirteen/tp_education_system/backend/config/navigation_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

shutil.copy(current_file, backup_file)
print(f"已备份当前菜单到: {backup_file}")

# 恢复备份菜单
restore_file = 'd:/erp_thirteen/tp_education_system/backend/config/navigation_backup_20260504_085022.json'
shutil.copy(restore_file, current_file)
print(f"已恢复菜单到: {restore_file}")

print("\n菜单已恢复！")
