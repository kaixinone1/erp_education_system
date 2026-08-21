@echo off
chcp 65001 >nul 2>&1
title 启动前端服务器

echo.
echo ========================================
echo     教育系统 - 启动前端服务器
echo ========================================
echo.
echo   前端端口: 5174
echo   API 代理: http://localhost:8001
echo.

:: ========== 清理前端端口 5174 ==========
echo [清理] 检查前端端口 5174...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5174.*LISTENING" 2^>nul') do (
    echo [清理] 终止占用 5174 端口的进程 PID=%%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo.
echo [启动] 前端服务器...
cd /d "d:\erp_fifteen\tp_education_system\frontend"
npx vite --port 5174 --host 0.0.0.0
pause