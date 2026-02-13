@echo off
chcp 65001
setlocal enabledelayedexpansion

echo 开始设置ERP系统备份任务...

:: 创建备份目录
if not exist "D:\backups\erp_system" (
    mkdir "D:\backups\erp_system"
    echo 创建备份目录: D:\backups\erp_system
)

:: 删除已存在的任务
echo 删除已存在的任务...
schtasks /delete /tn "ERP_System_Backup" /f 2>nul

:: 创建新的定时任务
echo 创建新的定时任务...
schtasks /create /tn "ERP_System_Backup" /tr "powershell.exe -ExecutionPolicy Bypass -File D:\erp_thirteen\full_backup.ps1" /sc hourly /mo 1 /ru SYSTEM /rl HIGHEST /f

if %errorlevel% equ 0 (
    echo.
    echo 定时任务创建成功!
    echo 任务名称: ERP_System_Backup
    echo 执行间隔: 每小时一次
    echo 备份位置: D:\backups\erp_system
    echo 日志文件: D:\backups\backup_log.txt
    echo.
    echo 查看任务: 任务计划程序 -^> ERP_System_Backup
) else (
    echo.
    echo 创建定时任务失败，请检查权限设置
)

pause
