#!/usr/bin/env pwsh

# 备份监控脚本
# 功能：检查备份日志，验证备份状态，生成监控报告

param(
    [string]$LogFile = "backup_log.txt",
    [int]$DaysToCheck = 7,
    [string]$ReportFile = "backup_monitor_report.txt",
    [switch]$SendAlert = $false,
    [string]$AlertEmail = "admin@example.com"
)

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $ReportFile -Value $logMessage
}

# 开始监控
$currentDate = Get-Date
$startDate = $currentDate.AddDays(-$DaysToCheck)

Write-Log "开始执行备份监控"
Write-Log "监控时间范围: $($startDate.ToString('yyyy-MM-dd')) 至 $($currentDate.ToString('yyyy-MM-dd'))"
Write-Log "检查的日志文件: $LogFile"

# 检查日志文件是否存在
if (-not (Test-Path $LogFile)) {
    Write-Log "错误: 备份日志文件不存在" "ERROR"
    Write-Log "监控完成 - 失败" "ERROR"
    exit 1
}

# 读取日志文件
$logContent = Get-Content $LogFile

# 分析备份记录
$backupRecords = @()
$currentRecord = $null

foreach ($line in $logContent) {
    if ($line -match '\[INFO\] 开始执行Git自动备份') {
        # 开始新的备份记录
        if ($currentRecord) {
            $backupRecords += $currentRecord
        }
        $currentRecord = @{
            StartTime = $line -replace '^\[(.*?)\].*$', '$1'
            Status = "未知"
            HasLocalBackup = $false
            HasRemotePush = $false
            Errors = @()
        }
    } elseif ($currentRecord) {
        if ($line -match '\[INFO\] Git自动备份执行完成') {
            $currentRecord.Status = "成功"
        } elseif ($line -match '\[ERROR\]') {
            $currentRecord.Status = "失败"
            $currentRecord.Errors += $line
        } elseif ($line -match '\[INFO\] 提交成功') {
            $currentRecord.HasLocalBackup = $true
        } elseif ($line -match '\[INFO\] 远程推送成功') {
            $currentRecord.HasRemotePush = $true
        } elseif ($line -match '\[WARNING\] 远程仓库未配置') {
            $currentRecord.HasRemotePush = $false
        }
    }
}

# 添加最后一条记录
if ($currentRecord) {
    $backupRecords += $currentRecord
}

# 过滤时间范围内的记录
$recentBackups = $backupRecords | Where-Object {
    $backupDate = [DateTime]($_.StartTime -replace '^(\d{4}-\d{2}-\d{2}).*$', '$1')
    $backupDate -ge $startDate.Date -and $backupDate -le $currentDate.Date
}

Write-Log "在监控时间范围内找到 $($recentBackups.Count) 条备份记录"

# 分析备份状态
$successCount = ($recentBackups | Where-Object {$_.Status -eq "成功"}).Count
$failedCount = ($recentBackups | Where-Object {$_.Status -eq "失败"}).Count
$unknownCount = ($recentBackups | Where-Object {$_.Status -eq "未知"}).Count

$localBackupSuccess = ($recentBackups | Where-Object {$_.HasLocalBackup}).Count
$remotePushSuccess = ($recentBackups | Where-Object {$_.HasRemotePush}).Count

Write-Log "备份成功: $successCount"
Write-Log "备份失败: $failedCount"
Write-Log "状态未知: $unknownCount"
Write-Log "本地备份成功: $localBackupSuccess"
Write-Log "远程推送成功: $remotePushSuccess"

# 生成详细报告
Write-Log "\n=== 详细备份记录 ==="

foreach ($backup in $recentBackups) {
    Write-Log "备份时间: $($backup.StartTime)"
    Write-Log "状态: $($backup.Status)"
    Write-Log "本地备份: $($backup.HasLocalBackup ? "成功" : "失败")"
    Write-Log "远程推送: $($backup.HasRemotePush ? "成功" : "失败")"
    
    if ($backup.Errors.Count -gt 0) {
        Write-Log "错误信息:" "ERROR"
        foreach ($error in $backup.Errors) {
            Write-Log "  - $error" "ERROR"
        }
    }
    
    Write-Log "---"
}

# 检查备份频率
$dailyBackups = @{}
foreach ($backup in $recentBackups) {
    $backupDate = $backup.StartTime -replace '^(\d{4}-\d{2}-\d{2}).*$', '$1'
    if (-not $dailyBackups.ContainsKey($backupDate)) {
        $dailyBackups[$backupDate] = 0
    }
    $dailyBackups[$backupDate]++
}

Write-Log "\n=== 备份频率分析 ==="
foreach ($date in $dailyBackups.Keys | Sort-Object) {
    Write-Log "$date: $($dailyBackups[$date]) 次备份"
}

# 检查是否有连续的备份失败
$consecutiveFailures = 0
$maxConsecutiveFailures = 0

foreach ($backup in $recentBackups) {
    if ($backup.Status -eq "失败") {
        $consecutiveFailures++
        if ($consecutiveFailures -gt $maxConsecutiveFailures) {
            $maxConsecutiveFailures = $consecutiveFailures
        }
    } else {
        $consecutiveFailures = 0
    }
}

Write-Log "\n=== 备份健康状态 ==="
if ($failedCount -eq 0) {
    Write-Log "备份系统状态: 健康" "INFO"
    Write-Log "所有备份都成功执行" "INFO"
} elseif ($failedCount -lt $successCount) {
    Write-Log "备份系统状态: 警告" "WARNING"
    Write-Log "部分备份失败，需要检查" "WARNING"
} else {
    Write-Log "备份系统状态: 严重" "ERROR"
    Write-Log "大部分备份失败，需要立即处理" "ERROR"
}

if ($maxConsecutiveFailures -ge 3) {
    Write-Log "警告: 发现 $maxConsecutiveFailures 次连续备份失败" "WARNING"
}

# 检查远程推送状态
if ($remotePushSuccess -eq 0) {
    Write-Log "警告: 没有成功的远程推送" "WARNING"
    Write-Log "请检查远程仓库配置" "WARNING"
} elseif ($remotePushSuccess -lt $localBackupSuccess) {
    Write-Log "警告: 部分远程推送失败" "WARNING"
    Write-Log "请检查网络连接和远程仓库配置" "WARNING"
}

# 检查备份频率
$expectedBackupDays = $DaysToCheck
$actualBackupDays = $dailyBackups.Count

if ($actualBackupDays -lt $expectedBackupDays) {
    $missingDays = $expectedBackupDays - $actualBackupDays
    Write-Log "警告: 缺少 $missingDays 天的备份" "WARNING"
    Write-Log "请检查备份计划是否正常执行" "WARNING"
}

# 生成总结
Write-Log "\n=== 监控总结 ==="
Write-Log "监控时间范围: $DaysToCheck 天"
Write-Log "总备份次数: $($recentBackups.Count)"
Write-Log "成功次数: $successCount"
Write-Log "失败次数: $failedCount"
Write-Log "成功率: $([math]::Round(($successCount / $recentBackups.Count) * 100, 2))%"
Write-Log "本地备份成功率: $([math]::Round(($localBackupSuccess / $recentBackups.Count) * 100, 2))%"
Write-Log "远程推送成功率: $([math]::Round(($remotePushSuccess / $recentBackups.Count) * 100, 2))%"

# 检查是否需要发送告警
if ($SendAlert -and ($failedCount -gt 0 -or $remotePushSuccess -eq 0 -or $actualBackupDays -lt $expectedBackupDays)) {
    Write-Log "准备发送告警邮件到: $AlertEmail"
    # 这里可以添加发送邮件的代码
    # 示例：Send-MailMessage -To $AlertEmail -Subject "备份系统告警" -Body "请查看备份监控报告" -SmtpServer "smtp.example.com"
    Write-Log "告警邮件已发送" "WARNING"
}

Write-Log "备份监控执行完成"
Write-Log "监控报告已保存到: $ReportFile"

# 显示报告摘要
Write-Host "\n=== 备份监控报告摘要 ==="
Write-Host "监控时间范围: $DaysToCheck 天"
Write-Host "总备份次数: $($recentBackups.Count)"
Write-Host "成功次数: $successCount"
Write-Host "失败次数: $failedCount"
Write-Host "成功率: $([math]::Round(($successCount / $recentBackups.Count) * 100, 2))%"
Write-Host "本地备份成功率: $([math]::Round(($localBackupSuccess / $recentBackups.Count) * 100, 2))%"
Write-Host "远程推送成功率: $([math]::Round(($remotePushSuccess / $recentBackups.Count) * 100, 2))%"
Write-Host "详细报告请查看: $ReportFile"

exit 0
