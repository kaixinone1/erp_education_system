@echo off
chcp 65001 >nul 2>&1
title 启动全部服务器

echo.
echo ========================================
echo     教育系统 - 启动全部服务器
echo ========================================
echo.
echo   前端端口: 5173
echo   后端端口: 8000
echo.
echo   正在启动...
echo.

set "SCRIPT_DIR=%~dp0"

echo [1/2] 启动后端服务器 (端口 8000)...
start "" /D "%SCRIPT_DIR%backend" cmd /k "cd /d "%SCRIPT_DIR%backend" && python main.py"

echo [2/2] 启动前端服务器 (端口 5173)...
start "" /D "%SCRIPT_DIR%frontend" cmd /k "cd /d "%SCRIPT_DIR%frontend" && npm run dev"

echo.
echo ========================================
echo   服务器已启动！
echo   前端: http://localhost:5173
echo   后端: http://localhost:8000
echo ========================================
echo.
echo   关闭各窗口即可停止对应服务器
echo.
pause
