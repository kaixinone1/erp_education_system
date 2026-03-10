@echo off
cd /d D:\erp_thirteen\tp_education_system\backend
start "Backend" cmd /k "python -m uvicorn main:app --port 8000 --host 127.0.0.1"

timeout /t 5 /nobreak

cd /d D:\erp_thirteen\tp_education_system\frontend
start "Frontend" cmd /k "npm run dev"
