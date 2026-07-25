@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 重启后端服务器...
echo 停止旧进程...
taskkill /f /fi "WINDOWTITLE eq 太平后端" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /f /pid %%a >nul 2>&1
timeout /t 2 /nobreak >nul

echo 启动后端...
cd /d tp_education_system\backend
start "太平后端" cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo 后端已启动: http://localhost:8000
pause