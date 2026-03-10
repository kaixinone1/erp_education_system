@echo off
chcp 936 >nul
title Education System - Service Monitor

cd /d "%~dp0"

echo ========================================
echo   Education System - Service Monitor
echo ========================================
echo.
echo This window will keep running to monitor servers
echo If servers crash, they will restart automatically
echo.
echo Press Ctrl+C to stop monitoring
echo.

:monitor_loop
:: Check backend server
tasklist /FI "WINDOWTITLE eq Education System Backend*" 2>nul | find /I "cmd.exe" >nul
if "%errorlevel%"=="1" (
    echo [%date% %time%] Backend server not running, restarting...
    start "Education System Backend" cmd /c "cd /d %~dp0tp_education_system\backend && python -m uvicorn main:app --port 8001 --host 127.0.0.1"
    timeout /t 3 /nobreak > nul
)

:: Check frontend server
tasklist /FI "WINDOWTITLE eq Education System Frontend*" 2>nul | find /I "cmd.exe" >nul
if "%errorlevel%"=="1" (
    echo [%date% %time%] Frontend server not running, restarting...
    start "Education System Frontend" cmd /c "cd /d %~dp0tp_education_system\frontend && npm run dev"
    timeout /t 5 /nobreak > nul
)

:: Check every 30 seconds
timeout /t 30 /nobreak > nul
goto monitor_loop
