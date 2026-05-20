@echo off
echo ========================================
echo 服务器自动重启脚本
echo ========================================

:restart
echo.
echo [%date% %time%] 启动后端服务器...
cd /d d:\erp_thirteen\tp_education_system\backend
start /b python main.py

echo.
echo [%date% %time%] 等待5秒检查服务器状态...
timeout /t 5 /nobreak >nul

:check
echo.
echo [%date% %time%] 检查服务器是否运行...
curl -s http://127.0.0.1:8000/api/todo-system/pending-triggers >nul 2>&1
if %errorlevel% equ 0 (
    echo [%date% %time%] 服务器运行正常
    timeout /t 30 /nobreak >nul
    goto check
) else (
    echo [%date% %time%] 服务器已崩溃，准备重启...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    goto restart
)
