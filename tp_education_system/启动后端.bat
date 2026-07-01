@echo off
chcp 65001 >nul 2>&1
title 启动后端服务器

set "SCRIPT_DIR=%~dp0"

echo.
echo ========================================
echo   启动后端服务器 (端口 8000)
echo ========================================
echo.
echo   工作目录: %SCRIPT_DIR%backend
echo.
echo   正在启动，请稍候...
echo.

cd /d "%SCRIPT_DIR%backend"
python main.py

pause
