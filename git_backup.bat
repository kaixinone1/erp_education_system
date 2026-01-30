@echo off

REM Git自动备份脚本
REM 功能：自动执行Git备份操作，包括添加、提交、分支管理和远程推送

setlocal

REM 设置变量
set BACKUP_BRANCH=backup
set MAIN_BRANCH=main
set REMOTE_NAME=origin
set PUSH_TO_REMOTE=true
set LOG_FILE=backup_log.txt

REM 生成时间戳
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set current_date=%%c-%%a-%%b)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set current_time=%%a:%%b)
set TIMESTAMP=%current_date% %current_time%
set COMMIT_MESSAGE=自动备份: %TIMESTAMP%

REM 日志函数
echo [%TIMESTAMP%] [INFO] 开始执行Git自动备份 >> %LOG_FILE%
echo [%TIMESTAMP%] [INFO] 备份分支: %BACKUP_BRANCH% >> %LOG_FILE%
echo [%TIMESTAMP%] [INFO] 主分支: %MAIN_BRANCH% >> %LOG_FILE%
echo [%TIMESTAMP%] [INFO] 远程推送: %PUSH_TO_REMOTE% >> %LOG_FILE%
echo [%TIMESTAMP%] [INFO] 远程仓库: %REMOTE_NAME% >> %LOG_FILE%
echo 开始执行Git自动备份
echo 备份分支: %BACKUP_BRANCH%
echo 主分支: %MAIN_BRANCH%
echo 远程推送: %PUSH_TO_REMOTE%
echo 远程仓库: %REMOTE_NAME%

REM 检查当前目录是否为Git仓库
if not exist ".git" (
    echo [%TIMESTAMP%] [ERROR] 错误: 当前目录不是Git仓库 >> %LOG_FILE%
    echo 错误: 当前目录不是Git仓库
    exit /b 1
)

REM 检查Git状态
echo [%TIMESTAMP%] [INFO] 检查Git状态 >> %LOG_FILE%
echo 检查Git状态
git status --porcelain > git_status.txt
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] Git操作失败 >> %LOG_FILE%
    echo Git操作失败
    exit /b 1
)

REM 检查是否有修改的文件
for /f "tokens=*" %%i in (git_status.txt) do (
    if not "%%i"=="" (
        echo [%TIMESTAMP%] [INFO] 发现修改的文件，开始添加和提交 >> %LOG_FILE%
        echo 发现修改的文件，开始添加和提交
        git add .
        git commit -m "%COMMIT_MESSAGE%"
        if %errorlevel% neq 0 (
            echo [%TIMESTAMP%] [ERROR] Git提交失败 >> %LOG_FILE%
            echo Git提交失败
            exit /b 1
        )
        echo [%TIMESTAMP%] [INFO] 提交成功 >> %LOG_FILE%
        echo 提交成功
        goto :check_branch
    )
)

echo [%TIMESTAMP%] [INFO] 没有发现修改的文件，跳过提交 >> %LOG_FILE%
echo 没有发现修改的文件，跳过提交

:check_branch
REM 检查并创建备份分支
echo [%TIMESTAMP%] [INFO] 检查并创建备份分支 >> %LOG_FILE%
echo 检查并创建备份分支

REM 检查备份分支是否存在
git branch | findstr "%BACKUP_BRANCH%" > nul
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [INFO] 创建备份分支: %BACKUP_BRANCH% >> %LOG_FILE%
    echo 创建备份分支: %BACKUP_BRANCH%
    git branch %BACKUP_BRANCH%
    if %errorlevel% neq 0 (
        echo [%TIMESTAMP%] [ERROR] 创建备份分支失败 >> %LOG_FILE%
        echo 创建备份分支失败
        exit /b 1
    )
) else (
    echo [%TIMESTAMP%] [INFO] 备份分支已存在: %BACKUP_BRANCH% >> %LOG_FILE%
    echo 备份分支已存在: %BACKUP_BRANCH%
)

REM 切换到备份分支
echo [%TIMESTAMP%] [INFO] 切换到备份分支 >> %LOG_FILE%
echo 切换到备份分支
git checkout %BACKUP_BRANCH%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] 切换分支失败 >> %LOG_FILE%
    echo 切换分支失败
    exit /b 1
)

REM 合并主分支
echo [%TIMESTAMP%] [INFO] 合并主分支到备份分支 >> %LOG_FILE%
echo 合并主分支到备份分支
git merge %MAIN_BRANCH% --no-ff -m "合并主分支到备份分支: %TIMESTAMP%"
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] 合并分支失败 >> %LOG_FILE%
    echo 合并分支失败
    exit /b 1
)

REM 切换回主分支
echo [%TIMESTAMP%] [INFO] 切换回主分支 >> %LOG_FILE%
echo 切换回主分支
git checkout %MAIN_BRANCH%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] 切换分支失败 >> %LOG_FILE%
    echo 切换分支失败
    exit /b 1
)

REM 推送到远程仓库
if "%PUSH_TO_REMOTE%"=="true" (
    echo [%TIMESTAMP%] [INFO] 推送到远程仓库: %REMOTE_NAME% >> %LOG_FILE%
    echo 推送到远程仓库: %REMOTE_NAME%
    
    REM 检查远程仓库是否存在
    git remote -v > remote_info.txt
    if %errorlevel% neq 0 (
        echo [%TIMESTAMP%] [ERROR] 检查远程仓库失败 >> %LOG_FILE%
        echo 检查远程仓库失败
    ) else (
        REM 检查是否有远程仓库配置
        findstr "%REMOTE_NAME%" remote_info.txt > nul
        if %errorlevel% neq 0 (
            echo [%TIMESTAMP%] [WARNING] 远程仓库未配置，跳过推送 >> %LOG_FILE%
            echo 远程仓库未配置，跳过推送
        ) else (
            REM 推送主分支
            echo [%TIMESTAMP%] [INFO] 推送主分支: %MAIN_BRANCH% >> %LOG_FILE%
            echo 推送主分支: %MAIN_BRANCH%
            git push %REMOTE_NAME% %MAIN_BRANCH%
            if %errorlevel% neq 0 (
                echo [%TIMESTAMP%] [ERROR] 推送主分支失败 >> %LOG_FILE%
                echo 推送主分支失败
            )
            
            REM 推送备份分支
            echo [%TIMESTAMP%] [INFO] 推送备份分支: %BACKUP_BRANCH% >> %LOG_FILE%
            echo 推送备份分支: %BACKUP_BRANCH%
            git push %REMOTE_NAME% %BACKUP_BRANCH%
            if %errorlevel% neq 0 (
                echo [%TIMESTAMP%] [ERROR] 推送备份分支失败 >> %LOG_FILE%
                echo 推送备份分支失败
            ) else (
                echo [%TIMESTAMP%] [INFO] 远程推送成功 >> %LOG_FILE%
                echo 远程推送成功
            )
        )
    )
)

REM 清理临时文件
del git_status.txt 2> nul
del remote_info.txt 2> nul

REM 完成
echo [%TIMESTAMP%] [INFO] Git自动备份执行完成 >> %LOG_FILE%
echo [%TIMESTAMP%] [INFO] ====================================== >> %LOG_FILE%
echo Git自动备份执行完成
echo ======================================

endlocal
