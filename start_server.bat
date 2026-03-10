@echo off
chcp 65001 >nul
title 教育管理系统 - 服务器管理

echo ========================================
echo   教育管理系统 - 服务器启动脚本
echo ========================================
echo.

:menu
echo 请选择操作:
echo [1] 启动服务器
echo [2] 查看服务器状态
echo [3] 停止所有服务器
echo [4] 重启服务器
echo [5] 退出
echo.

set /p choice=请输入选项 (1-5):

if "%choice%"=="1" goto start
if "%choice%"=="2" goto status
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto restart
if "%choice%"=="5" exit

echo 无效选项，请重新选择
echo.
goto menu

:start
echo.
echo [1/2] 正在启动后端服务器...
cd /d "%~dp0tp_education_system\backend"
start /B cmd /c "python -m uvicorn main:app --port 8000 --host 127.0.0.1"

timeout /t 3 /nobreak > nul

echo [2/2] 正在启动前端服务器...
cd /d "%~dp0tp_education_system\frontend"
start /B cmd /c "npm run dev"

timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo   服务器启动完成！
echo ========================================
echo   后端: http://127.0.0.1:8000
echo   前端: http://localhost:5173
echo ========================================
echo.
echo 正在打开浏览器...
start http://localhost:5173
goto menu

:status
echo.
echo 正在检查服务器状态...
powershell -Command "Get-NetTCPConnection -LocalPort 8000,5173 -ErrorAction SilentlyContinue | Select-Object LocalPort,State"
echo.
goto menu

:stop
echo.
echo 正在停止所有服务器...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
taskkill /F /IM node.exe 2>nul
echo 服务器已停止
echo.
goto menu

:restart
echo.
echo 正在重启服务器...
goto stop
timeout /t 2 /nobreak > nul
goto start
