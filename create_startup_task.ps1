# Create Education System Startup Task

$taskName = "Education System Auto Start"
$scriptPath = "D:\erp_thirteen\start_edu_system.bat"

# Check if task exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task exists, removing old task..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create task action
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c start /min `"$scriptPath`""

# Create task trigger (at logon)
$trigger = New-ScheduledTaskTrigger -AtLogon

# Create task settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Create task
$task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings

# Register task
Register-ScheduledTask -TaskName $taskName -InputObject $task -Force

Write-Host "======================================"
Write-Host "  Startup task created successfully!"
Write-Host "======================================"
Write-Host "Task Name: $taskName"
Write-Host "Script Path: $scriptPath"
Write-Host "Trigger: At logon"
Write-Host "======================================"
Write-Host ""
Write-Host "Manage task:"
Write-Host "1. Open Task Scheduler (taskschd.msc)"
Write-Host "2. Find task: $taskName"
Write-Host "3. Disable, delete or modify"
Write-Host ""
Read-Host "Press Enter to exit"
