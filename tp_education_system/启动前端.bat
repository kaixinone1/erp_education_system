@echo off
chcp 65001 >nul 2>&1
title 启动前端服务器

set "SCRIPT_DIR=%~dp0"

echo.
echo ========================================
echo   启动前端服务器 (端口 5173)
echo ========================================
echo.
echo   工作目录: %SCRIPT_DIR%frontend
echo.
echo   正在启动，请稍候...
echo.

cd /d "%SCRIPT_DIR%frontend"
npm run dev

pause
