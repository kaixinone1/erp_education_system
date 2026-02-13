#!/usr/bin/env pwsh

# 完整备份脚本 - 备份代码、数据库、配置文件

param(
    [string]$BackupDir = "D:\backups\erp_system",
    [string]$LogFile = "D:\backups\backup_log.txt",
    [int]$KeepDays = 30
)

# 日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage -ErrorAction SilentlyContinue
}

# 创建备份目录
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backupPath = Join-Path $BackupDir $timestamp
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

Write-Log "开始完整备份"
Write-Log "备份目录: $backupPath"

# 1. 备份代码
Write-Log "开始备份代码..."
try {
    $codeBackupPath = Join-Path $backupPath "code"
    New-Item -ItemType Directory -Path $codeBackupPath -Force | Out-Null
    
    # Git bundle备份
    $bundleFile = Join-Path $codeBackupPath "repository.bundle"
    git bundle create $bundleFile --all 2>&1 | Out-Null
    
    # 项目文件备份
    $projectBackupPath = Join-Path $codeBackupPath "project"
    Copy-Item -Path "D:\erp_thirteen\*" -Destination $projectBackupPath -Recurse -Force -Exclude @("venv", "node_modules", "__pycache__", ".git")
    
    Write-Log "代码备份完成"
} catch {
    Write-Log "代码备份失败: $($_.Exception.Message)" "ERROR"
}

# 2. 备份数据库
Write-Log "开始备份数据库..."
try {
    $dbBackupPath = Join-Path $backupPath "database"
    New-Item -ItemType Directory -Path $dbBackupPath -Force | Out-Null
    
    $dbFile = Join-Path $dbBackupPath "taiping_education.sql"
    $env:PGPASSWORD = "taiping_password"
    pg_dump -h localhost -U taiping_user -d taiping_education -f $dbFile 2>&1 | Out-Null
    
    if (Test-Path $dbFile) {
        Write-Log "数据库备份完成"
    } else {
        Write-Log "数据库备份失败" "ERROR"
    }
} catch {
    Write-Log "数据库备份失败: $($_.Exception.Message)" "ERROR"
}

# 3. 备份配置文件
Write-Log "开始备份配置文件..."
try {
    $configBackupPath = Join-Path $backupPath "configs"
    New-Item -ItemType Directory -Path $configBackupPath -Force | Out-Null
    
    # 复制配置目录
    $configDirs = @(
        "D:\erp_thirteen\tp_education_system\backend\config",
        "D:\erp_thirteen\tp_education_system\frontend\src\config"
    )
    foreach ($dir in $configDirs) {
        if (Test-Path $dir) {
            Copy-Item -Path $dir -Destination $configBackupPath -Recurse -Force
        }
    }
    
    Write-Log "配置文件备份完成"
} catch {
    Write-Log "配置文件备份失败: $($_.Exception.Message)" "ERROR"
}

# 4. 创建备份信息
$backupInfo = @{
    backup_time = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    git_commit = git rev-parse HEAD 2>$null
    git_branch = git branch --show-current 2>$null
}
$backupInfo | ConvertTo-Json | Out-File -FilePath (Join-Path $backupPath "backup_info.json") -Encoding UTF8

# 5. 清理旧备份
Write-Log "清理旧备份..."
try {
    $cutoffDate = (Get-Date).AddDays(-$KeepDays)
    Get-ChildItem -Path $BackupDir -Directory | Where-Object { $_.CreationTime -lt $cutoffDate } | ForEach-Object {
        Remove-Item -Path $_.FullName -Recurse -Force
        Write-Log "删除旧备份: $($_.Name)"
    }
} catch {
    Write-Log "清理旧备份失败: $($_.Exception.Message)" "WARNING"
}

Write-Log "完整备份执行完成: $backupPath"
Write-Log "======================================"
