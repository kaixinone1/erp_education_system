@echo off
chcp 65001 >nul 2>&1
title 启动后端服务器

echo.
echo ========================================
echo     教育系统 - 启动后端服务器
echo ========================================
echo.
echo   后端端口: 8001
echo   数据库: taiping_education_fifteen
echo.

:: ========== 清理后端端口 8001 ==========
echo [清理] 检查后端端口 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001.*LISTENING" 2^>nul') do (
    echo [清理] 终止占用 8001 端口的进程 PID=%%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo.
echo [启动] 后端服务器...
cd /d "d:\erp_fifteen\tp_education_system\backend"
python main.py
pause