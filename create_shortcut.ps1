$s = (New-Object -COM WScript.Shell).CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\EducationSystem.lnk")
$s.TargetPath = "D:\erp_thirteen\auto_start.bat"
$s.WorkingDirectory = "D:\erp_thirteen"
$s.Save()
Write-Host "Shortcut created"
