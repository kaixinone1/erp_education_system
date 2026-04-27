# 每日自动备份脚本
# 包含：Git提交 + 数据库备份

$backupDir = "D:\erp_thirteen\backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "$backupDir\backup_$timestamp.log"

# 创建备份目录
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# 开始备份
"========================================" | Tee-Object -FilePath $logFile
"  每日自动备份 - $timestamp" | Tee-Object -FilePath $logFile -Append
"========================================" | Tee-Object -FilePath $logFile -Append
"" | Tee-Object -FilePath $logFile -Append

# 1. Git备份
"[1/2] Git备份..." | Tee-Object -FilePath $logFile -Append
try {
    Set-Location "D:\erp_thirteen"
    
    # 检查是否有修改
    $status = git status --porcelain
    if ($status) {
        git add -A
        git commit -m "自动备份: $timestamp" | Tee-Object -FilePath $logFile -Append
        "  ✓ Git备份完成" | Tee-Object -FilePath $logFile -Append
    } else {
        "  ℹ 没有修改，跳过Git备份" | Tee-Object -FilePath $logFile -Append
    }
} catch {
    "  ✗ Git备份失败: $_" | Tee-Object -FilePath $logFile -Append
}

"" | Tee-Object -FilePath $logFile -Append

# 2. 数据库备份
"[2/2] 数据库备份..." | Tee-Object -FilePath $logFile -Append
try {
    $dbBackupFile = "$backupDir\db_backup_$timestamp.sql"
    $env:PGPASSWORD = "taiping_password"
    
    & pg_dump -h localhost -U taiping_user -d taiping_education -f $dbBackupFile 2>&1
    
    if (Test-Path $dbBackupFile) {
        "  ✓ 数据库备份完成: $dbBackupFile" | Tee-Object -FilePath $logFile -Append
    } else {
        "  ✗ 数据库备份失败" | Tee-Object -FilePath $logFile -Append
    }
} catch {
    "  ✗ 数据库备份失败: $_" | Tee-Object -FilePath $logFile -Append
}

"" | Tee-Object -FilePath $logFile -Append
"========================================" | Tee-Object -FilePath $logFile -Append
"  备份完成" | Tee-Object -FilePath $logFile -Append
"========================================" | Tee-Object -FilePath $logFile -Append

# 清理旧备份（保留30天）
Get-ChildItem "$backupDir\db_backup_*.sql" | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force
Get-ChildItem "$backupDir\backup_*.log" | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force
