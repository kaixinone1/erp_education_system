# Education System Server Startup Script

$backendPath = "D:\erp_thirteen\tp_education_system\backend"
$frontendPath = "D:\erp_thirteen\tp_education_system\frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Education System Server Manager" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if servers are already running
$backendRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*Backend*" }
$frontendRunning = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*Frontend*" }

if ($backendRunning) {
    Write-Host "[Warning] Backend server already running" -ForegroundColor Yellow
} else {
    Write-Host "[1/2] Starting backend server..." -ForegroundColor Green
    Start-Process -FilePath "powershell" -ArgumentList "-Command `"cd '$backendPath'; python -m uvicorn main:app --port 8001 --host 127.0.0.1`"" -WindowStyle Minimized
    Start-Sleep -Seconds 3
}

if ($frontendRunning) {
    Write-Host "[Warning] Frontend server already running" -ForegroundColor Yellow
} else {
    Write-Host "[2/2] Starting frontend server..." -ForegroundColor Green
    Start-Process -FilePath "powershell" -ArgumentList "-Command `"cd '$frontendPath'; npm run dev`"" -WindowStyle Minimized
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Education System Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Backend: http://127.0.0.1:8001"
Write-Host "  Frontend: http://localhost:5173"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to close this window (servers will keep running)"
