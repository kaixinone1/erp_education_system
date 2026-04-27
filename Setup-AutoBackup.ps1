# 设置每日自动备份任务

$taskName = "ErpThirteen_DailyBackup"
$scriptPath = "D:\erp_thirteen\auto_backup_daily.ps1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  设置每日自动备份任务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否以管理员运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "[警告] 建议以管理员身份运行，以确保任务能正常创建" -ForegroundColor Yellow
    Write-Host ""
}

# 删除旧任务
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "删除旧任务..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# 创建新任务
Write-Host "创建每日备份任务..." -ForegroundColor Green

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""

# 每天下午6点执行
$trigger = New-ScheduledTaskTrigger -Daily -At "18:00"

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings

Register-ScheduledTask -TaskName $taskName -InputObject $task -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  自动备份任务创建成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "任务名称: $taskName"
Write-Host "执行时间: 每天 18:00"
Write-Host "备份脚本: $scriptPath"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "管理任务:"
Write-Host "  1. 打开任务计划程序 (taskschd.msc)"
Write-Host "  2. 找到任务: $taskName"
Write-Host "  3. 可修改时间或禁用任务"
Write-Host ""

# 询问是否立即测试
$testNow = Read-Host "是否立即运行一次备份测试? (y/n)"
if ($testNow -eq "y" -or $testNow -eq "Y") {
    Write-Host ""
    Write-Host "开始测试备份..." -ForegroundColor Cyan
    & powershell -ExecutionPolicy Bypass -File $scriptPath
}

Write-Host ""
Read-Host "按 Enter 退出"
