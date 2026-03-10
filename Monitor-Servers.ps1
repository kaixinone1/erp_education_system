# Education System Server Monitor
# This script keeps running and restarts servers if they crash

$backendPath = "D:\erp_thirteen\tp_education_system\backend"
$frontendPath = "D:\erp_thirteen\tp_education_system\frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Education System Server Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This window monitors server status." -ForegroundColor Yellow
Write-Host "If servers crash, they will restart automatically." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Red
Write-Host ""

while ($true) {
    # Check backend server
    $backendRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*Backend*" -or $_.CommandLine -like "*uvicorn*" }
    if (-not $backendRunning) {
        Write-Host "[$(Get-Date)] Backend server not running, restarting..." -ForegroundColor Red
        Start-Process -FilePath "powershell" -ArgumentList "-Command `"cd '$backendPath'; python -m uvicorn main:app --port 8001 --host 127.0.0.1`"" -WindowStyle Minimized
        Start-Sleep -Seconds 3
    }
    
    # Check frontend server
    $frontendRunning = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*Frontend*" -or $_.CommandLine -like "*npm*" }
    if (-not $frontendRunning) {
        Write-Host "[$(Get-Date)] Frontend server not running, restarting..." -ForegroundColor Red
        Start-Process -FilePath "powershell" -ArgumentList "-Command `"cd '$frontendPath'; npm run dev`"" -WindowStyle Minimized
        Start-Sleep -Seconds 5
    }
    
    # Check every 30 seconds
    Start-Sleep -Seconds 30
}
