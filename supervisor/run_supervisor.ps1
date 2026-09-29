# ERP Supervisor Launcher (PowerShell version)
# This script bridges Task Scheduler and supervisor.py
# Solves environment issues when running pythonw.exe/python.exe from Task Scheduler

$ErrorActionPreference = "Continue"
$supervisorDir = "d:\erp_fifteen\supervisor"
$supervisorScript = Join-Path $supervisorDir "supervisor.py"
$startupErrorLog = Join-Path $supervisorDir "logs\startup_error.log"
$debugLog = Join-Path $supervisorDir "logs\launcher_debug.log"

# Ensure log directory exists
$logDir = Join-Path $supervisorDir "logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

# Write debug info
$debugMsg = "[{0}] Launcher started, user: {1}, cwd: {2}" -f (Get-Date), $env:USERNAME, (Get-Location)
Add-Content -Path $debugLog -Value $debugMsg

# Find Python
$pythonCandidates = @(
    "C:\Users\lmmwg\Miniconda3\python.exe",
    "C:\Users\lmmwg\AppData\Local\Programs\Python\Python313\python.exe",
    "python.exe"
)
$pythonExe = $null
foreach ($p in $pythonCandidates) {
    if (Test-Path $p) { $pythonExe = $p; break }
    $cmd = Get-Command $p -ErrorAction SilentlyContinue
    if ($cmd) { $pythonExe = $cmd.Source; break }
}

if (-not $pythonExe) {
    $msg = "[{0}] ERROR: Python interpreter not found" -f (Get-Date)
    Add-Content -Path $startupErrorLog -Value $msg
    Add-Content -Path $debugLog -Value $msg
    exit 1
}

Add-Content -Path $debugLog -Value ("[{0}] Python path: {1}" -f (Get-Date), $pythonExe)

# Set working directory
Set-Location $supervisorDir
Add-Content -Path $debugLog -Value ("[{0}] Working directory set: {1}" -f (Get-Date), (Get-Location))

# Set environment variables
$env:PYTHONPATH = $supervisorDir
$env:PYTHONIOENCODING = "utf-8"

# Run supervisor script
Add-Content -Path $debugLog -Value ("[{0}] Starting: {1} {2}" -f (Get-Date), $pythonExe, $supervisorScript)
try {
    $output = & $pythonExe $supervisorScript 2>&1
    $exitCode = $LASTEXITCODE
    Add-Content -Path $debugLog -Value ("[{0}] Script finished, exit code: {1}" -f (Get-Date), $exitCode)
    if ($output) {
        $outputStr = $output | Out-String
        if ($outputStr.Length -gt 500) { $outputStr = $outputStr.Substring(0, 500) + "..." }
        Add-Content -Path $debugLog -Value ("[{0}] Output: {1}" -f (Get-Date), $outputStr)
    }
    exit $exitCode
}
catch {
    $msg = "[{0}] Launcher exception: {1}" -f (Get-Date), $_
    Add-Content -Path $startupErrorLog -Value $msg
    Add-Content -Path $debugLog -Value $msg
    exit 1
}
