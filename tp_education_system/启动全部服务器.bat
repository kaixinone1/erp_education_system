@echo off
chcp 65001 >nul 2>&1
title 启动全部服务器

echo.
echo ========================================
echo     教育系统 - 启动全部服务器
echo ========================================
echo.
echo   前端端口: 5174
echo   后端端口: 8001
echo.
echo   正在清理旧进程并启动...
echo.

set "SCRIPT_DIR=%~dp0"

:: ========== 清理后端端口 8001 ==========
echo [清理] 检查后端端口 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001.*LISTENING" 2^>nul') do (
    echo [清理] 终止占用 8001 端口的进程 PID=%%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

:: ========== 清理前端端口 5174 ==========
echo [清理] 检查前端端口 5174...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5174.*LISTENING" 2^>nul') do (
    echo [清理] 终止占用 5174 端口的进程 PID=%%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo.
echo [1/2] 启动后端服务器 (端口 8001)...
start "" /D "%SCRIPT_DIR%backend" cmd /k "cd /d "%SCRIPT_DIR%backend" && python main.py"

echo [2/2] 启动前端服务器 (端口 5174)...
start "" /D "%SCRIPT_DIR%frontend" cmd /k "cd /d "%SCRIPT_DIR%frontend" && npm run dev"

echo.
echo ========================================
echo   服务器已启动！
echo   前端: http://localhost:5174
echo   后端: http://localhost:8001
echo ========================================
echo.
echo   关闭各窗口即可停止对应服务器
echo.
pause