# Setup Education System Auto Start

$taskName = "EduSystemAutoStart"
$scriptPath = "D:\erp_thirteen\Start-Servers.ps1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Education System Auto Start Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "[Warning] Not running as Administrator. Task will be created for current user only." -ForegroundColor Yellow
    Write-Host ""
}

# Menu
Write-Host "Select option:" -ForegroundColor White
Write-Host "[1] Create auto start task (Recommended)"
Write-Host "[2] Copy to Startup folder"
Write-Host "[3] Remove auto start"
Write-Host "[4] Exit"
Write-Host ""

$choice = Read-Host "Enter option (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Creating scheduled task..." -ForegroundColor Green
        
        # Remove existing task
        $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        }
        
        # Create task
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Minimized -File `"$scriptPath`""
        $trigger = New-ScheduledTaskTrigger -AtLogon
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
        $task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings
        
        try {
            Register-ScheduledTask -TaskName $taskName -InputObject $task -Force
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  Auto start task created!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "Task Name: $taskName"
            Write-Host "Trigger: At user logon"
            Write-Host "========================================" -ForegroundColor Green
        } catch {
            Write-Host ""
            Write-Host "[Error] Failed to create task: $_" -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Copying to Startup folder..." -ForegroundColor Green
        
        $startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
        $shortcutPath = "$startupPath\Start-EduSystem.lnk"
        
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($shortcutPath)
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Minimized -File `"$scriptPath`""
        $Shortcut.WorkingDirectory = "D:\erp_thirteen"
        $Shortcut.Save()
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  Added to Startup folder!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Shortcut: $shortcutPath"
        Write-Host "========================================" -ForegroundColor Green
    }
    
    "3" {
        Write-Host ""
        Write-Host "Removing auto start..." -ForegroundColor Yellow
        
        # Remove scheduled task
        $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            Write-Host "Removed scheduled task" -ForegroundColor Green
        }
        
        # Remove startup shortcut
        $startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
        Remove-Item -Path "$startupPath\Start-EduSystem.lnk" -ErrorAction SilentlyContinue
        Write-Host "Removed startup shortcut" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  Auto start removed!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    }
    
    "4" {
        exit
    }
    
    default {
        Write-Host ""
        Write-Host "[Error] Invalid option" -ForegroundColor Red
    }
}

Write-Host ""
Read-Host "Press Enter to exit"
