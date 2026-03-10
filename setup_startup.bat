@echo off
chcp 65001 >nul
title 教育管理系统 - 设置开机启动

cd /d "%~dp0"

echo ========================================
echo   教育管理系统 - 设置开机启动
echo ========================================
echo.

echo 请选择启动方式:
echo [1] 创建开机启动任务（推荐）
echo [2] 复制到启动文件夹
echo [3] 创建桌面快捷方式
echo [4] 创建监控服务（自动重启）
echo [5] 取消开机启动
echo [6] 退出
echo.

set /p choice=请输入选项 (1-6):

if "%choice%"=="1" goto task_scheduler
if "%choice%"=="2" goto startup_folder
if "%choice%"=="3" goto desktop_shortcut
if "%choice%"=="4" goto monitor_service
if "%choice%"=="5" goto remove_startup
if "%choice%"=="6" exit

echo 无效选项
goto end

:task_scheduler
echo.
echo 正在创建任务计划程序任务...
powershell -ExecutionPolicy Bypass -File "%~dp0create_startup_task.ps1"
goto end

:startup_folder
echo.
echo 正在复制到启动文件夹...
copy /Y "%~dp0start_edu_system.bat" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
echo 已添加到启动文件夹
echo.
pause
goto end

:desktop_shortcut
echo.
echo 正在创建桌面快捷方式...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\教育管理系统.lnk'); $Shortcut.TargetPath = '%~dp0start_edu_system.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"
echo 桌面快捷方式已创建
echo.
pause
goto end

:monitor_service
echo.
echo 正在创建监控服务...
copy /Y "%~dp0monitor_service.bat" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
echo 监控服务已添加到启动文件夹
echo 监控窗口将在开机后自动打开
echo.
pause
goto end

:remove_startup
echo.
echo 正在取消开机启动...
del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\start_edu_system.bat" 2>nul
del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\monitor_service.bat" 2>nul
powershell -Command "Unregister-ScheduledTask -TaskName '教育管理系统自动启动' -Confirm:$false -ErrorAction SilentlyContinue"
echo 开机启动已取消
echo.
pause
goto end

:end
echo.
echo ========================================
echo   设置完成
echo ========================================
echo.
