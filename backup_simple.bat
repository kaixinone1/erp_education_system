@echo off
chcp 65001
setlocal

set BACKUP_DIR=D:\backups\erp_system
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_PATH=%BACKUP_DIR%\%TIMESTAMP%

echo 开始备份...
echo 备份路径: %BACKUP_PATH%

:: 创建备份目录
mkdir "%BACKUP_PATH%\code" 2>nul
mkdir "%BACKUP_PATH%\database" 2>nul
mkdir "%BACKUP_PATH%\configs" 2>nul

:: 1. 备份代码
echo 备份代码...
cd /d D:\erp_thirteen
git bundle create "%BACKUP_PATH%\code\repository.bundle" --all 2>nul
xcopy /E /I /Y /EXCLUDE:D:\erp_thirteen\backup_exclude.txt "D:\erp_thirteen\*" "%BACKUP_PATH%\code\project\" 2>nul

:: 2. 备份数据库
echo 备份数据库...
set PGPASSWORD=taiping_password
pg_dump -h localhost -U taiping_user -d taiping_education -f "%BACKUP_PATH%\database\taiping_education.sql" 2>nul

:: 3. 备份配置
echo 备份配置文件...
xcopy /E /I /Y "D:\erp_thirteen\tp_education_system\backend\config" "%BACKUP_PATH%\configs\backend_config\" 2>nul
xcopy /E /I /Y "D:\erp_thirteen\tp_education_system\frontend\src\config" "%BACKUP_PATH%\configs\frontend_config\" 2>nul

:: 4. 创建备份信息
echo {"backup_time": "%date% %time%"} > "%BACKUP_PATH%\backup_info.json"

echo 备份完成: %BACKUP_PATH%
pause
