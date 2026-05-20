import json

# 读取当前菜单
with open('d:/erp_thirteen/tp_education_system/backend/config/navigation.json', 'r', encoding='utf-8') as f:
    current_nav = json.load(f)

# 读取备份菜单
with open('d:/erp_thirteen/tp_education_system/backend/config/navigation_backup_20260504_085022.json', 'r', encoding='utf-8') as f:
    backup_nav = json.load(f)

def compare_menus(current, backup, path=""):
    """递归对比菜单差异"""
    differences = []
    
    # 检查当前菜单中新增的项
    for item in current:
        item_id = item.get('id')
        item_title = item.get('title')
        
        # 在备份中查找对应的项
        found = False
        for backup_item in backup:
            if backup_item.get('id') == item_id:
                found = True
                break
        
        if not found:
            differences.append({
                'type': '新增',
                'path': f"{path}/{item_title}",
                'id': item_id,
                'title': item_title
            })
    
    # 检查备份菜单中被删除的项
    for backup_item in backup:
        backup_id = backup_item.get('id')
        backup_title = backup_item.get('title')
        
        # 在当前菜单中查找对应的项
        found = False
        for item in current:
            if item.get('id') == backup_id:
                found = True
                # 递归检查子菜单
                if 'children' in item and 'children' in backup_item:
                    child_diffs = compare_menus(
                        item['children'], 
                        backup_item['children'], 
                        f"{path}/{item_title}"
                    )
                    differences.extend(child_diffs)
                break
        
        if not found:
            differences.append({
                'type': '删除',
                'path': f"{path}/{backup_title}",
                'id': backup_id,
                'title': backup_title
            })
    
    return differences

print("="*80)
print("菜单对比分析")
print("="*80)

differences = compare_menus(current_nav['modules'], backup_nav['modules'])

if differences:
    print("\n发现以下差异：\n")
    for diff in differences:
        print(f"[{diff['type']}] {diff['path']}")
        print(f"  ID: {diff['id']}")
        print(f"  标题: {diff['title']}")
        print()
else:
    print("\n没有发现差异，菜单未被修改。")
