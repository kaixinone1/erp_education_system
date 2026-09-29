<#
.SYNOPSIS
    卸载 ERP 系统监督脚本任务
.DESCRIPTION
    从 Windows 任务计划程序中移除名为 ERP_Supervisor_Watchdog 的定时任务。
.NOTES
    使用管理员权限运行此脚本。
#>

# 必须管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "错误：请使用管理员权限运行此脚本" -ForegroundColor Red
    exit 1
}

$taskName = "ERP_Supervisor_Watchdog"

Write-Host "卸载 ERP 监督任务..." -ForegroundColor Cyan

# 检查任务是否存在
if (-not (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue)) {
    Write-Host "ℹ️ 任务 $taskName 不存在，无需卸载" -ForegroundColor Yellow
    exit 0
}

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "✅ 监督任务已卸载" -ForegroundColor Green
}
catch {
    Write-Host "❌ 卸载失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "注意：监督脚本文件本身未删除，路径 d:\erp_fifteen\supervisor\" -ForegroundColor Yellow
Write-Host "如需彻底删除，请手动删除该目录" -ForegroundColor Yellow
