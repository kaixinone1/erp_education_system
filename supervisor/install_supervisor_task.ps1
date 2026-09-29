<#
.SYNOPSIS
    Install ERP Supervisor Watchdog to Windows Task Scheduler
.DESCRIPTION
    Creates a scheduled task named ERP_Supervisor_Watchdog that runs every 30 minutes.
    The supervisor checks backend health, scheduler status, backup freshness, and notification status.
.NOTES
    Run this script as Administrator.
    To uninstall, run uninstall_supervisor_task.ps1
#>

# Must run as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Please run this script as Administrator" -ForegroundColor Red
    exit 1
}

# Configuration
$taskName = "ERP_Supervisor_Watchdog"
$launcherScript = "d:\erp_fifteen\supervisor\run_supervisor.ps1"
$supervisorDir = "d:\erp_fifteen\supervisor"

# Check if launcher script exists
if (-not (Test-Path $launcherScript)) {
    Write-Host "ERROR: Launcher script not found: $launcherScript" -ForegroundColor Red
    exit 1
}

Write-Host "Installing ERP Supervisor Watchdog..." -ForegroundColor Cyan
Write-Host "  Task Name: $taskName"
Write-Host "  Launcher: $launcherScript"
Write-Host "  Interval: 30 minutes"
Write-Host ""

# Task action: run PowerShell launcher
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$launcherScript`"" `
    -WorkingDirectory $supervisorDir

# Trigger: every 30 minutes, repeat for 10 years
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 30) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

# Settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

# Principal: run as current user
$user = "$env:USERDOMAIN\$env:USERNAME"
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited

# Register task
try {
    # Unregister old task if exists
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Write-Host "Removing old task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }

    Register-ScheduledTask -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force | Out-Null

    Write-Host "SUCCESS: Task installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Get-ScheduledTask -TaskName $taskName | Format-List TaskName, State
    Get-ScheduledTaskInfo -TaskName $taskName | Format-List LastRunTime, NextRunTime, LastTaskResult
}
catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Trigger manually: schtasks /Run /TN $taskName"
Write-Host "  2. Check log: d:\erp_fifteen\supervisor\logs\supervisor.log"
Write-Host "  3. Configure webhook: edit d:\erp_fifteen\supervisor\config\supervisor_config.json"
