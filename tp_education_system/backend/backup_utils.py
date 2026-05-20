import os
import shutil
from datetime import datetime

def backup_before_modify(file_path, description=""):
    """修改文件前自动备份"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.path.dirname(file_path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    filename = os.path.basename(file_path)
    backup_path = os.path.join(backup_dir, f"{filename}.backup_{timestamp}")
    
    shutil.copy2(file_path, backup_path)
    
    log_file = os.path.join(backup_dir, "backup_log.txt")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{datetime.now()} - 备份: {filename}\n")
        f.write(f"  原文件: {file_path}\n")
        f.write(f"  备份文件: {backup_path}\n")
        f.write(f"  说明: {description}\n")
    
    print(f"✅ 已备份: {backup_path}")
    return backup_path

def restore_from_backup(backup_path, target_path):
    """从备份恢复文件"""
    if not os.path.exists(backup_path):
        print(f"备份文件不存在: {backup_path}")
        return False
    
    shutil.copy2(backup_path, target_path)
    print(f"✅ 已恢复: {target_path}")
    return True

if __name__ == "__main__":
    print("备份工具使用示例：")
    print("backup_before_modify('path/to/file.py', '修改前备份')")
