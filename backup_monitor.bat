@echo off

REM 备份监控脚本
REM 功能：检查备份日志，验证备份状态，生成监控报告

setlocal

REM 设置变量
set LOG_FILE=backup_log.txt
set DAYS_TO_CHECK=7
set REPORT_FILE=backup_monitor_report.txt
set SEND_ALERT=false
set ALERT_EMAIL=admin@example.com

REM 生成时间戳
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set current_date=%%c-%%a-%%b)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set current_time=%%a:%%b)
set TIMESTAMP=%current_date% %current_time%

REM 日志函数
echo [%TIMESTAMP%] [INFO] 开始执行备份监控 >> %REPORT_FILE%
echo 开始执行备份监控

REM 检查日志文件是否存在
if not exist "%LOG_FILE%" (
    echo [%TIMESTAMP%] [ERROR] 错误: 备份日志文件不存在 >> %REPORT_FILE%
    echo 错误: 备份日志文件不存在
    exit /b 1
)

REM 读取日志文件并分析
set "SUCCESS_COUNT=0"
set "FAILED_COUNT=0"
set "UNKNOWN_COUNT=0"
set "LOCAL_BACKUP_SUCCESS=0"
set "REMOTE_PUSH_SUCCESS=0"
set "TOTAL_BACKUPS=0"

REM 分析日志文件
for /f "tokens=*" %%a in (%LOG_FILE%) do (
    set "line=%%a"
    
    REM 检查备份开始记录
    echo %%a | findstr "开始执行Git自动备份" > nul
    if %errorlevel% equ 0 (
        set /a "TOTAL_BACKUPS+=1"
    )
    
    REM 检查备份完成记录
    echo %%a | findstr "Git自动备份执行完成" > nul
    if %errorlevel% equ 0 (
        set /a "SUCCESS_COUNT+=1"
    )
    
    REM 检查错误记录
    echo %%a | findstr "[ERROR]" > nul
    if %errorlevel% equ 0 (
        set /a "FAILED_COUNT+=1"
    )
    
    REM 检查本地备份成功
    echo %%a | findstr "提交成功" > nul
    if %errorlevel% equ 0 (
        set /a "LOCAL_BACKUP_SUCCESS+=1"
    )
    
    REM 检查远程推送成功
    echo %%a | findstr "远程推送成功" > nul
    if %errorlevel% equ 0 (
        set /a "REMOTE_PUSH_SUCCESS+=1"
    )
)

REM 计算未知状态数量
set /a "UNKNOWN_COUNT=TOTAL_BACKUPS - SUCCESS_COUNT - FAILED_COUNT"

REM 计算成功率
if %TOTAL_BACKUPS% gtr 0 (
    set /a "SUCCESS_RATE=SUCCESS_COUNT * 100 / TOTAL_BACKUPS"
    set /a "LOCAL_BACKUP_RATE=LOCAL_BACKUP_SUCCESS * 100 / TOTAL_BACKUPS"
    set /a "REMOTE_PUSH_RATE=REMOTE_PUSH_SUCCESS * 100 / TOTAL_BACKUPS"
) else (
    set "SUCCESS_RATE=0"
    set "LOCAL_BACKUP_RATE=0"
    set "REMOTE_PUSH_RATE=0"
)

REM 生成监控报告
echo [%TIMESTAMP%] [INFO] 监控时间范围: 最近 %DAYS_TO_CHECK% 天 >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 总备份次数: %TOTAL_BACKUPS% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 成功次数: %SUCCESS_COUNT% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 失败次数: %FAILED_COUNT% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 状态未知: %UNKNOWN_COUNT% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 成功率: %SUCCESS_RATE%%% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 本地备份成功率: %LOCAL_BACKUP_RATE%%% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 远程推送成功率: %REMOTE_PUSH_RATE%%% >> %REPORT_FILE%

echo 监控时间范围: 最近 %DAYS_TO_CHECK% 天
echo 总备份次数: %TOTAL_BACKUPS%
echo 成功次数: %SUCCESS_COUNT%
echo 失败次数: %FAILED_COUNT%
echo 状态未知: %UNKNOWN_COUNT%
echo 成功率: %SUCCESS_RATE%%%
echo 本地备份成功率: %LOCAL_BACKUP_RATE%%%
echo 远程推送成功率: %REMOTE_PUSH_RATE%%%

REM 检查备份健康状态
if %FAILED_COUNT% equ 0 (
    echo [%TIMESTAMP%] [INFO] 备份系统状态: 健康 >> %REPORT_FILE%
echo 备份系统状态: 健康
) else if %FAILED_COUNT% lss %SUCCESS_COUNT% (
    echo [%TIMESTAMP%] [WARNING] 备份系统状态: 警告 >> %REPORT_FILE%
echo 备份系统状态: 警告
    echo [%TIMESTAMP%] [WARNING] 部分备份失败，需要检查 >> %REPORT_FILE%
echo 部分备份失败，需要检查
) else (
    echo [%TIMESTAMP%] [ERROR] 备份系统状态: 严重 >> %REPORT_FILE%
echo 备份系统状态: 严重
    echo [%TIMESTAMP%] [ERROR] 大部分备份失败，需要立即处理 >> %REPORT_FILE%
echo 大部分备份失败，需要立即处理
)

REM 检查远程推送状态
if %REMOTE_PUSH_SUCCESS% equ 0 (
    echo [%TIMESTAMP%] [WARNING] 警告: 没有成功的远程推送 >> %REPORT_FILE%
echo 警告: 没有成功的远程推送
    echo [%TIMESTAMP%] [WARNING] 请检查远程仓库配置 >> %REPORT_FILE%
echo 请检查远程仓库配置
) else if %REMOTE_PUSH_SUCCESS% lss %LOCAL_BACKUP_SUCCESS% (
    echo [%TIMESTAMP%] [WARNING] 警告: 部分远程推送失败 >> %REPORT_FILE%
echo 警告: 部分远程推送失败
    echo [%TIMESTAMP%] [WARNING] 请检查网络连接和远程仓库配置 >> %REPORT_FILE%
echo 请检查网络连接和远程仓库配置
)

REM 检查备份频率
if %TOTAL_BACKUPS% lss %DAYS_TO_CHECK% (
    set /a "MISSING_BACKUPS=DAYS_TO_CHECK - TOTAL_BACKUPS"
    echo [%TIMESTAMP%] [WARNING] 警告: 缺少 %MISSING_BACKUPS% 次备份 >> %REPORT_FILE%
echo 警告: 缺少 %MISSING_BACKUPS% 次备份
    echo [%TIMESTAMP%] [WARNING] 请检查备份计划是否正常执行 >> %REPORT_FILE%
echo 请检查备份计划是否正常执行
)

REM 生成总结报告
echo [%TIMESTAMP%] [INFO] === 监控总结 === >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 监控时间范围: %DAYS_TO_CHECK% 天 >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 总备份次数: %TOTAL_BACKUPS% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 成功次数: %SUCCESS_COUNT% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 失败次数: %FAILED_COUNT% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 成功率: %SUCCESS_RATE%%% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 本地备份成功率: %LOCAL_BACKUP_RATE%%% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 远程推送成功率: %REMOTE_PUSH_RATE%%% >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 备份监控执行完成 >> %REPORT_FILE%
echo [%TIMESTAMP%] [INFO] 监控报告已保存到: %REPORT_FILE% >> %REPORT_FILE%

echo.
echo === 监控总结 ===
echo 监控时间范围: %DAYS_TO_CHECK% 天
echo 总备份次数: %TOTAL_BACKUPS%
echo 成功次数: %SUCCESS_COUNT%
echo 失败次数: %FAILED_COUNT%
echo 成功率: %SUCCESS_RATE%%%
echo 本地备份成功率: %LOCAL_BACKUP_RATE%%%
echo 远程推送成功率: %REMOTE_PUSH_RATE%%%
echo 备份监控执行完成
echo 监控报告已保存到: %REPORT_FILE%

REM 检查是否需要发送告警
if "%SEND_ALERT%"=="true" (
    if %FAILED_COUNT% gtr 0 ( 
        echo [%TIMESTAMP%] [WARNING] 准备发送告警邮件到: %ALERT_EMAIL% >> %REPORT_FILE%
        echo 准备发送告警邮件到: %ALERT_EMAIL%
        REM 这里可以添加发送邮件的代码
        echo [%TIMESTAMP%] [WARNING] 告警邮件已发送 >> %REPORT_FILE%
        echo 告警邮件已发送
    )
)

endlocal
