#!/usr/bin/env pwsh

# 设置备份定时任务
# 功能：创建Windows计划任务，每小时执行一次备份

param(
    [string]$BackupScript = "D:\erp_thirteen\full_backup.ps1",
    [string]$TaskName = "ERP_System_Backup",
    [int]$IntervalHours = 1
)

Write-Host "开始设置备份定时任务..."
Write-Host "备份脚本: $BackupScript"
Write-Host "任务名称: $TaskName"
Write-Host "执行间隔: $IntervalHours 小时"

# 检查备份脚本是否存在
if (-not (Test-Path $BackupScript)) {
    Write-Error "备份脚本不存在: $BackupScript"
    exit 1
}

# 创建备份目录
$backupDir = "D:\backups\erp_system"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Write-Host "创建备份目录: $backupDir"
}

# 删除已存在的任务
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "删除已存在的任务: $TaskName"
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 创建任务操作
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$BackupScript`""

# 创建任务触发器（每小时执行一次）
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours $IntervalHours) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

# 创建任务设置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false

# 注册任务
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "ERP系统自动备份任务 - 每小时执行一次完整备份（代码+数据库+配置）" `
        -RunLevel Highest `
        -Force

    Write-Host "定时任务创建成功!"
    Write-Host "任务名称: $TaskName"
    Write-Host "执行间隔: $IntervalHours 小时"
    Write-Host "下次执行时间: $((Get-ScheduledTask -TaskName $TaskName).Triggers[0].StartBoundary)"
    
    # 立即执行一次测试
    Write-Host ""
    Write-Host "是否立即执行一次备份测试? (y/n)"
    $response = Read-Host
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "开始执行备份测试..."
        & powershell.exe -ExecutionPolicy Bypass -File $BackupScript
    }
    
} catch {
    Write-Error "创建定时任务失败: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Host "备份系统设置完成!"
Write-Host "查看任务: 任务计划程序 -> $TaskName"
Write-Host "备份位置: D:\backups\erp_system"
Write-Host "日志文件: D:\backups\backup_log.txt"
Write-Host "======================================"

exit 0
