@echo off
chcp 936 >nul
title Stop Education System

echo ========================================
echo   Stopping Education System...
echo ========================================
echo.

echo [1/2] Stopping backend server...
taskkill /F /FI "WINDOWTITLE eq Education System Backend*" /IM cmd.exe 2>nul
taskkill /F /IM python.exe 2>nul
echo Backend server stopped

echo.
echo [2/2] Stopping frontend server...
taskkill /F /FI "WINDOWTITLE eq Education System Frontend*" /IM cmd.exe 2>nul
taskkill /F /IM node.exe 2>nul
echo Frontend server stopped

echo.
echo ========================================
echo   Education System Stopped
echo ========================================
echo.
pause
