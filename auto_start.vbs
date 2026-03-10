Set WshShell = CreateObject("WScript.Shell")

' 启动后端服务器（隐藏窗口）
WshShell.Run "cmd /c cd /d D:\erp_thirteen\tp_education_system\backend && python -m uvicorn main:app --port 8000 --host 127.0.0.1", 0, False

' 等待5秒
WScript.Sleep 5000

' 启动前端服务器（隐藏窗口）
WshShell.Run "cmd /c cd /d D:\erp_thirteen\tp_education_system\frontend && npm run dev", 0, False

Set WshShell = Nothing
