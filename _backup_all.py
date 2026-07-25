import subprocess, os, datetime

# 备份目录
backup_dir = r"d:\erp_thirteen\备份"
os.makedirs(backup_dir, exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
sql_file = os.path.join(backup_dir, f"taiping_education_{timestamp}.sql")

# 使用 pg_dump 备份数据库
print("正在备份数据库...")
pg_dump_path = r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe"
if not os.path.exists(pg_dump_path):
    # 尝试其他路径
    import glob
    candidates = glob.glob(r"C:\Program Files\PostgreSQL\*\bin\pg_dump.exe")
    if candidates:
        pg_dump_path = candidates[0]
    else:
        print("错误: 找不到 pg_dump.exe")
        exit(1)

cmd = [
    pg_dump_path,
    "-h", "localhost",
    "-p", "5432",
    "-U", "taiping_user",
    "-d", "taiping_education",
    "-f", sql_file,
    "--encoding", "UTF8",
    "--no-owner",
    "--no-privileges"
]

env = os.environ.copy()
env["PGPASSWORD"] = "taiping_password"

result = subprocess.run(cmd, capture_output=True, text=True, env=env)
if result.returncode == 0:
    size_mb = os.path.getsize(sql_file) / (1024 * 1024)
    print(f"数据库备份成功: {sql_file}")
    print(f"文件大小: {size_mb:.2f} MB")
else:
    print(f"备份失败: {result.stderr}")
    exit(1)

# 同时备份关键配置文件
import shutil
config_backup = os.path.join(backup_dir, f"config_backup_{timestamp}")
os.makedirs(config_backup, exist_ok=True)
config_files = [
    r"d:\erp_thirteen\tp_education_system\backend\config\navigation.json",
    r"d:\erp_thirteen\tp_education_system\backend\config\merged_schema_mappings.json",
    r"d:\erp_thirteen\tp_education_system\backend\config\table_name_mappings.json",
    r"d:\erp_thirteen\tp_education_system\backend\config\field_mappings.json",
]
for cf in config_files:
    if os.path.exists(cf):
        dest = os.path.join(config_backup, os.path.basename(cf))
        shutil.copy2(cf, dest)
        print(f"配置备份: {os.path.basename(cf)}")

print("\n全部备份完成！")