$s = (New-Object -COM WScript.Shell).CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\EducationSystem.lnk")
$s.TargetPath = "wscript.exe"
$s.Arguments = "D:\erp_thirteen\auto_start.vbs"
$s.WorkingDirectory = "D:\erp_thirteen"
$s.Save()
Write-Host "VBS shortcut created"
