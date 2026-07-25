@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 重启前端服务器...
echo 停止旧进程...
taskkill /f /fi "WINDOWTITLE eq 太平前端" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /f /pid %%a >nul 2>&1
timeout /t 2 /nobreak >nul

echo 启动前端...
cd /d tp_education_system\frontend
start "太平前端" cmd /c "npx vite --host 0.0.0.0 --port 5173"
echo 前端已启动: http://localhost:5173
pause