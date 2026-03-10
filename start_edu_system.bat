@echo off
chcp 936 >nul
title Education System Service

cd /d "%~dp0"

echo ========================================
echo   Education System - Server Manager
echo ========================================
echo.

:: Check if already running
tasklist /FI "WINDOWTITLE eq Education System Backend*" 2>nul | find /I "cmd.exe" >nul
if "%errorlevel%"=="0" (
    echo [Warning] Backend server already running
) else (
    echo [1/2] Starting backend server...
    start "Education System Backend" cmd /c "cd /d %~dp0tp_education_system\backend && python -m uvicorn main:app --port 8001 --host 127.0.0.1"
    timeout /t 3 /nobreak > nul
)

tasklist /FI "WINDOWTITLE eq Education System Frontend*" 2>nul | find /I "cmd.exe" >nul
if "%errorlevel%"=="0" (
    echo [Warning] Frontend server already running
) else (
    echo [2/2] Starting frontend server...
    start "Education System Frontend" cmd /c "cd /d %~dp0tp_education_system\frontend && npm run dev"
    timeout /t 5 /nobreak > nul
)

echo.
echo ========================================
echo   Education System Started
echo ========================================
echo   Backend: http://127.0.0.1:8001
echo   Frontend: http://localhost:5173
echo ========================================
echo.

echo Press any key to close this window (servers will keep running)...
pause > nul
