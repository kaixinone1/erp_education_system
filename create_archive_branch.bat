@echo off

REM 自动创建归档分支脚本
REM 功能：根据版本管理策略创建归档分支并推送到远程仓库

setlocal

REM 设置变量
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set current_date=%%c-%%a-%%b)
set MainBranch=main
set RemoteName=origin
set CreateTag=true
set TagName=v%current_date:~0,4%.%current_date:~5,2%.%current_date:~8,2%
set TagMessage=归档版本: %current_date%
set LogFile=archive_branch_log.txt
set ArchiveBranch=archive/%current_date%

REM 生成时间戳
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set current_time=%%a:%%b)
set TIMESTAMP=%current_date% %current_time%

REM 日志函数
echo [%TIMESTAMP%] [INFO] 开始执行归档分支创建 >> %LogFile%
echo 开始执行归档分支创建
echo [%TIMESTAMP%] [INFO] 归档日期: %current_date% >> %LogFile%
echo 归档日期: %current_date%
echo [%TIMESTAMP%] [INFO] 主分支: %MainBranch% >> %LogFile%
echo 主分支: %MainBranch%
echo [%TIMESTAMP%] [INFO] 远程仓库: %RemoteName% >> %LogFile%
echo 远程仓库: %RemoteName%
echo [%TIMESTAMP%] [INFO] 创建标签: %CreateTag% >> %LogFile%
echo 创建标签: %CreateTag%
echo [%TIMESTAMP%] [INFO] 标签名称: %TagName% >> %LogFile%
echo 标签名称: %TagName%
echo [%TIMESTAMP%] [INFO] 归档分支名称: %ArchiveBranch% >> %LogFile%
echo 归档分支名称: %ArchiveBranch%

REM 检查当前目录是否为Git仓库
if not exist ".git" (
    echo [%TIMESTAMP%] [ERROR] 错误: 当前目录不是Git仓库 >> %LogFile%
    echo 错误: 当前目录不是Git仓库
    exit /b 1
)

REM 切换到主分支
echo [%TIMESTAMP%] [INFO] 切换到主分支: %MainBranch% >> %LogFile%
echo 切换到主分支: %MainBranch%
git checkout %MainBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] 错误: 切换到主分支失败 >> %LogFile%
    echo 错误: 切换到主分支失败
    exit /b 1
)

REM 拉取最新代码
echo [%TIMESTAMP%] [INFO] 拉取最新代码 >> %LogFile%
echo 拉取最新代码
git pull %RemoteName% %MainBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [WARNING] 警告: 拉取代码失败，可能是网络问题 >> %LogFile%
    echo 警告: 拉取代码失败，可能是网络问题
    echo [%TIMESTAMP%] [INFO] 继续执行归档分支创建 >> %LogFile%
    echo 继续执行归档分支创建
)

REM 检查归档分支是否已存在
echo [%TIMESTAMP%] [INFO] 检查归档分支是否已存在 >> %LogFile%
echo 检查归档分支是否已存在
git branch -a > branches.txt
findstr "%ArchiveBranch%" branches.txt > nul
if %errorlevel% equ 0 (
    echo [%TIMESTAMP%] [WARNING] 警告: 归档分支已存在，将删除并重新创建 >> %LogFile%
    echo 警告: 归档分支已存在，将删除并重新创建
    REM 删除本地分支
    git branch -D %ArchiveBranch%
    REM 删除远程分支（如果存在）
    git push %RemoteName% --delete %ArchiveBranch% 2>nul
)

REM 创建归档分支
echo [%TIMESTAMP%] [INFO] 创建归档分支: %ArchiveBranch% >> %LogFile%
echo 创建归档分支: %ArchiveBranch%
git checkout -b %ArchiveBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] 错误: 创建归档分支失败 >> %LogFile%
    echo 错误: 创建归档分支失败
    exit /b 1
)

REM 推送归档分支到远程仓库
echo [%TIMESTAMP%] [INFO] 推送归档分支到远程仓库 >> %LogFile%
echo 推送归档分支到远程仓库
git push %RemoteName% %ArchiveBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [WARNING] 警告: 推送归档分支失败，可能是网络问题 >> %LogFile%
    echo 警告: 推送归档分支失败，可能是网络问题
    echo [%TIMESTAMP%] [INFO] 归档分支已在本地创建，但未推送到远程 >> %LogFile%
    echo 归档分支已在本地创建，但未推送到远程
) else (
    echo [%TIMESTAMP%] [INFO] 成功: 归档分支已推送到远程仓库 >> %LogFile%
    echo 成功: 归档分支已推送到远程仓库
)

REM 创建标签
if "%CreateTag%"=="true" (
    echo [%TIMESTAMP%] [INFO] 创建版本标签: %TagName% >> %LogFile%
    echo 创建版本标签: %TagName%
    git tag -a %TagName% -m "%TagMessage%"
    if %errorlevel% neq 0 (
        echo [%TIMESTAMP%] [WARNING] 警告: 创建标签失败 >> %LogFile%
        echo 警告: 创建标签失败
    ) else (
        echo [%TIMESTAMP%] [INFO] 推送标签到远程仓库 >> %LogFile%
        echo 推送标签到远程仓库
        git push %RemoteName% %TagName%
        if %errorlevel% neq 0 (
            echo [%TIMESTAMP%] [WARNING] 警告: 推送标签失败，可能是网络问题 >> %LogFile%
            echo 警告: 推送标签失败，可能是网络问题
            echo [%TIMESTAMP%] [INFO] 标签已在本地创建，但未推送到远程 >> %LogFile%
            echo 标签已在本地创建，但未推送到远程
        ) else (
            echo [%TIMESTAMP%] [INFO] 成功: 标签已推送到远程仓库 >> %LogFile%
            echo 成功: 标签已推送到远程仓库
        )
    )
)

REM 切换回主分支
echo [%TIMESTAMP%] [INFO] 切换回主分支: %MainBranch% >> %LogFile%
echo 切换回主分支: %MainBranch%
git checkout %MainBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [WARNING] 警告: 切换回主分支失败 >> %LogFile%
    echo 警告: 切换回主分支失败
)

REM 显示分支状态
echo [%TIMESTAMP%] [INFO] 显示当前分支状态 >> %LogFile%
echo 显示当前分支状态
git branch

REM 生成总结
echo [%TIMESTAMP%] [INFO] === 归档分支创建总结 === >> %LogFile%
echo [%TIMESTAMP%] [INFO] 归档日期: %current_date% >> %LogFile%
echo [%TIMESTAMP%] [INFO] 归档分支: %ArchiveBranch% >> %LogFile%
echo [%TIMESTAMP%] [INFO] 主分支: %MainBranch% >> %LogFile%
echo [%TIMESTAMP%] [INFO] 远程仓库: %RemoteName% >> %LogFile%
echo [%TIMESTAMP%] [INFO] 创建标签: %CreateTag% >> %LogFile%
echo [%TIMESTAMP%] [INFO] 归档分支创建完成 >> %LogFile%
echo [%TIMESTAMP%] [INFO] 日志文件: %LogFile% >> %LogFile%

echo.
echo === 归档分支创建总结 ===
echo 归档日期: %current_date%
echo 归档分支: %ArchiveBranch%
echo 主分支: %MainBranch%
echo 远程仓库: %RemoteName%
echo 创建标签: %CreateTag%
echo 归档分支创建完成
echo 日志文件: %LogFile%

REM 清理临时文件
del branches.txt 2>nul

endlocal
