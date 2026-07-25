@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo  太平镇教育人事管理系统 - 服务器启动脚本
echo ========================================
echo.
echo 前端: http://localhost:5173
echo 后端: http://localhost:8000
echo 按 Ctrl+C 停止所有服务器
echo.

:start_backend
echo [后端] 启动中...
start "太平后端" cmd /c "cd /d tp_education_system\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo [后端] 已启动

:start_frontend
echo [前端] 启动中...
start "太平前端" cmd /c "cd /d tp_education_system\frontend && npx vite --host 0.0.0.0 --port 5173"
echo [前端] 已启动

echo.
echo ========================================
echo  服务器已启动，可以开始使用
echo ========================================
pause