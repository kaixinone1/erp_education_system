@echo off
chcp 936 >nul
title Education System Startup Setup

cd /d "%~dp0"

echo ========================================
echo   Education System - Startup Setup
echo ========================================
echo.

echo Select startup method:
echo [1] Create Task Scheduler (Recommended)
echo [2] Copy to Startup Folder
echo [3] Create Desktop Shortcut
echo [4] Create Monitor Service (Auto-restart)
echo [5] Remove Startup
echo [6] Exit
echo.

set /p choice=Enter option (1-6):

if "%choice%"=="1" goto task_scheduler
if "%choice%"=="2" goto startup_folder
if "%choice%"=="3" goto desktop_shortcut
if "%choice%"=="4" goto monitor_service
if "%choice%"=="5" goto remove_startup
if "%choice%"=="6" exit

echo Invalid option
goto end

:task_scheduler
echo.
echo Creating Task Scheduler task...
powershell -ExecutionPolicy Bypass -File "%~dp0create_startup_task.ps1"
goto end

:startup_folder
echo.
echo Copying to Startup folder...
copy /Y "%~dp0start_edu_system.bat" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
echo Added to Startup folder
echo.
pause
goto end

:desktop_shortcut
echo.
echo Creating Desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Education System.lnk'); $Shortcut.TargetPath = '%~dp0start_edu_system.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"
echo Desktop shortcut created
echo.
pause
goto end

:monitor_service
echo.
echo Creating Monitor Service...
copy /Y "%~dp0monitor_service.bat" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
echo Monitor service added to Startup folder
echo Monitor window will open automatically after boot
echo.
pause
goto end

:remove_startup
echo.
echo Removing Startup...
del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\start_edu_system.bat" 2>nul
del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\monitor_service.bat" 2>nul
powershell -Command "Unregister-ScheduledTask -TaskName 'Education System Auto Start' -Confirm:$false -ErrorAction SilentlyContinue"
echo Startup removed
echo.
pause
goto end

:end
echo.
echo ========================================
echo   Setup Complete
echo ========================================
echo.
