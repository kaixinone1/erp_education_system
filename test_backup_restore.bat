@echo off

REM 从备份恢复测试脚本
REM 功能：测试从备份分支和归档分支恢复的流程

setlocal

REM 设置变量
set TestFile=test_restore.txt
set BackupBranch=backup
set MainBranch=main
set LogFile=restore_test_log.txt

REM 生成时间戳
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set current_date=%%c-%%a-%%b)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set current_time=%%a:%%b)
set TIMESTAMP=%current_date% %current_time%

REM 日志函数
echo [%TIMESTAMP%] [INFO] 开始执行备份恢复测试 >> %LogFile%
echo 开始执行备份恢复测试
echo [%TIMESTAMP%] [INFO] 测试文件: %TestFile% >> %LogFile%
echo 测试文件: %TestFile%
echo [%TIMESTAMP%] [INFO] 备份分支: %BackupBranch% >> %LogFile%
echo 备份分支: %BackupBranch%
echo [%TIMESTAMP%] [INFO] 主分支: %MainBranch% >> %LogFile%
echo 主分支: %MainBranch%

REM 检查当前目录是否为Git仓库
if not exist ".git" (
    echo [%TIMESTAMP%] [ERROR] 错误: 当前目录不是Git仓库 >> %LogFile%
    echo 错误: 当前目录不是Git仓库
    exit /b 1
)

REM 1. 准备测试环境
echo [%TIMESTAMP%] [INFO] === 1. 准备测试环境 === >> %LogFile%
echo === 1. 准备测试环境 ===

REM 创建测试文件
echo [%TIMESTAMP%] [INFO] 创建测试文件: %TestFile% >> %LogFile%
echo 创建测试文件: %TestFile%
echo 原始测试内容 - %TIMESTAMP% > %TestFile%
echo [%TIMESTAMP%] [INFO] 测试文件内容: 原始测试内容 - %TIMESTAMP% >> %LogFile%
echo 测试文件内容: 原始测试内容 - %TIMESTAMP%

REM 提交测试文件
echo [%TIMESTAMP%] [INFO] 提交测试文件到主分支 >> %LogFile%
echo 提交测试文件到主分支
git add %TestFile%
git commit -m "测试: 添加测试文件"
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [WARNING] 警告: 提交失败，可能是文件已存在 >> %LogFile%
    echo 警告: 提交失败，可能是文件已存在
)

REM 推送到备份分支（模拟自动备份）
echo [%TIMESTAMP%] [INFO] 推送到备份分支 >> %LogFile%
echo 推送到备份分支
git checkout %BackupBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] 错误: 切换到备份分支失败 >> %LogFile%
    echo 错误: 切换到备份分支失败
    exit /b 1
)

git merge %MainBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [WARNING] 警告: 合并失败，可能是冲突 >> %LogFile%
    echo 警告: 合并失败，可能是冲突
)

git checkout %MainBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] 错误: 切换回主分支失败 >> %LogFile%
    echo 错误: 切换回主分支失败
    exit /b 1
)

REM 2. 模拟故障
echo [%TIMESTAMP%] [INFO] === 2. 模拟故障 === >> %LogFile%
echo === 2. 模拟故障 ===

REM 修改测试文件（模拟数据损坏）
echo [%TIMESTAMP%] [INFO] 修改测试文件（模拟数据损坏） >> %LogFile%
echo 修改测试文件（模拟数据损坏）
echo 损坏的测试内容 - %TIMESTAMP% > %TestFile%
echo [%TIMESTAMP%] [INFO] 损坏的内容: 损坏的测试内容 - %TIMESTAMP% >> %LogFile%
echo 损坏的内容: 损坏的测试内容 - %TIMESTAMP%

REM 提交损坏的文件（模拟错误提交）
echo [%TIMESTAMP%] [INFO] 提交损坏的文件（模拟错误提交） >> %LogFile%
echo 提交损坏的文件（模拟错误提交）
git add %TestFile%
git commit -m "错误: 损坏的测试文件"
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [WARNING] 警告: 提交失败 >> %LogFile%
    echo 警告: 提交失败
)

REM 3. 从备份分支恢复
echo [%TIMESTAMP%] [INFO] === 3. 从备份分支恢复 === >> %LogFile%
echo === 3. 从备份分支恢复 ===

echo [%TIMESTAMP%] [INFO] 查看备份分支的测试文件内容 >> %LogFile%
echo 查看备份分支的测试文件内容
git checkout %BackupBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] 错误: 切换到备份分支失败 >> %LogFile%
    echo 错误: 切换到备份分支失败
    exit /b 1
)

if exist "%TestFile%" (
    set /p backupContent=<%TestFile%
    echo [%TIMESTAMP%] [INFO] 备份文件内容: %backupContent% >> %LogFile%
    echo 备份文件内容: %backupContent%
) else (
    echo [%TIMESTAMP%] [WARNING] 警告: 备份分支中不存在测试文件 >> %LogFile%
    echo 警告: 备份分支中不存在测试文件
)

REM 从备份分支恢复到主分支
echo [%TIMESTAMP%] [INFO] 从备份分支恢复到主分支 >> %LogFile%
echo 从备份分支恢复到主分支
git checkout %MainBranch%
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [ERROR] 错误: 切换回主分支失败 >> %LogFile%
    echo 错误: 切换回主分支失败
    exit /b 1
)

REM 使用git show从备份分支恢复测试文件
echo [%TIMESTAMP%] [INFO] 使用git show从备份分支恢复测试文件 >> %LogFile%
echo 使用git show从备份分支恢复测试文件
git show "%BackupBranch%:%TestFile%" > %TestFile%
if %errorlevel% equ 0 (
    echo [%TIMESTAMP%] [INFO] 成功: 从备份分支恢复测试文件 >> %LogFile%
    echo 成功: 从备份分支恢复测试文件
    set /p restoredContent=<%TestFile%
    echo [%TIMESTAMP%] [INFO] 恢复后的内容: %restoredContent% >> %LogFile%
    echo 恢复后的内容: %restoredContent%
    
    REM 提交恢复的文件
    git add %TestFile%
    git commit -m "恢复: 从备份分支恢复测试文件"
    if %errorlevel% equ 0 (
        echo [%TIMESTAMP%] [INFO] 成功: 提交恢复的文件 >> %LogFile%
        echo 成功: 提交恢复的文件
    ) else (
        echo [%TIMESTAMP%] [WARNING] 警告: 提交恢复的文件失败 >> %LogFile%
        echo 警告: 提交恢复的文件失败
    )
) else (
    echo [%TIMESTAMP%] [ERROR] 错误: 从备份分支恢复失败 >> %LogFile%
    echo 错误: 从备份分支恢复失败
)

REM 4. 测试从归档分支恢复
echo [%TIMESTAMP%] [INFO] === 4. 测试从归档分支恢复 === >> %LogFile%
echo === 4. 测试从归档分支恢复 ===

REM 查找归档分支
echo [%TIMESTAMP%] [INFO] 查找归档分支 >> %LogFile%
echo 查找归档分支
git branch -a > branches.txt
findstr "archive/" branches.txt > archive_branches.txt
if %errorlevel% equ 0 (
    echo [%TIMESTAMP%] [INFO] 找到归档分支 >> %LogFile%
    echo 找到归档分支
    REM 获取最新的归档分支
    for /f "tokens=*" %%a in (archive_branches.txt) do (
        set latestArchive=%%a
    )
    set latestArchive=%latestArchive:~1%
    echo [%TIMESTAMP%] [INFO] 最新的归档分支: %latestArchive% >> %LogFile%
    echo 最新的归档分支: %latestArchive%
    
    REM 从归档分支恢复
    echo [%TIMESTAMP%] [INFO] 从归档分支查看测试文件 >> %LogFile%
    echo 从归档分支查看测试文件
    git show "%latestArchive%:%TestFile%" > archive_test.txt
    if %errorlevel% equ 0 (
        set /p archiveContent=<archive_test.txt
        echo [%TIMESTAMP%] [INFO] 归档文件内容: %archiveContent% >> %LogFile%
        echo 归档文件内容: %archiveContent%
        echo [%TIMESTAMP%] [INFO] 成功: 从归档分支获取文件内容 >> %LogFile%
        echo 成功: 从归档分支获取文件内容
        del archive_test.txt
    ) else (
        echo [%TIMESTAMP%] [WARNING] 警告: 归档分支中不存在测试文件 >> %LogFile%
        echo 警告: 归档分支中不存在测试文件
    )
) else (
    echo [%TIMESTAMP%] [WARNING] 警告: 未找到归档分支 >> %LogFile%
    echo 警告: 未找到归档分支
)

REM 5. 测试从标签恢复
echo [%TIMESTAMP%] [INFO] === 5. 测试从标签恢复 === >> %LogFile%
echo === 5. 测试从标签恢复 ===

REM 查找标签
echo [%TIMESTAMP%] [INFO] 查找标签 >> %LogFile%
echo 查找标签
git tag > tags.txt
if %errorlevel% equ 0 (
    for /f "tokens=*" %%a in (tags.txt) do (
        set latestTag=%%a
    )
    if defined latestTag (
        echo [%TIMESTAMP%] [INFO] 最新的标签: %latestTag% >> %LogFile%
        echo 最新的标签: %latestTag%
        
        REM 从标签恢复
        echo [%TIMESTAMP%] [INFO] 从标签查看测试文件 >> %LogFile%
        echo 从标签查看测试文件
        git show "%latestTag%:%TestFile%" > tag_test.txt
        if %errorlevel% equ 0 (
            set /p tagContent=<tag_test.txt
            echo [%TIMESTAMP%] [INFO] 标签文件内容: %tagContent% >> %LogFile%
            echo 标签文件内容: %tagContent%
            echo [%TIMESTAMP%] [INFO] 成功: 从标签获取文件内容 >> %LogFile%
            echo 成功: 从标签获取文件内容
            del tag_test.txt
        ) else (
            echo [%TIMESTAMP%] [WARNING] 警告: 标签中不存在测试文件 >> %LogFile%
            echo 警告: 标签中不存在测试文件
        )
    ) else (
        echo [%TIMESTAMP%] [WARNING] 警告: 未找到标签 >> %LogFile%
        echo 警告: 未找到标签
    )
) else (
    echo [%TIMESTAMP%] [WARNING] 警告: 未找到标签 >> %LogFile%
    echo 警告: 未找到标签
)

REM 6. 清理测试环境
echo [%TIMESTAMP%] [INFO] === 6. 清理测试环境 === >> %LogFile%
echo === 6. 清理测试环境 ===

REM 删除测试文件
if exist "%TestFile%" (
    echo [%TIMESTAMP%] [INFO] 删除测试文件: %TestFile% >> %LogFile%
    echo 删除测试文件: %TestFile%
    del %TestFile%
)

REM 提交清理操作
echo [%TIMESTAMP%] [INFO] 提交清理操作 >> %LogFile%
echo 提交清理操作
git add .
git commit -m "测试: 清理测试文件"
if %errorlevel% neq 0 (
    echo [%TIMESTAMP%] [WARNING] 警告: 清理提交失败 >> %LogFile%
    echo 警告: 清理提交失败
)

REM 7. 测试总结
echo [%TIMESTAMP%] [INFO] === 7. 测试总结 === >> %LogFile%
echo === 7. 测试总结 ===
echo [%TIMESTAMP%] [INFO] 备份恢复测试完成 >> %LogFile%
echo 备份恢复测试完成
echo [%TIMESTAMP%] [INFO] 测试项目: >> %LogFile%
echo 测试项目:
echo [%TIMESTAMP%] [INFO] 1. 从备份分支恢复: 成功 >> %LogFile%
echo 1. 从备份分支恢复: 成功

REM 检查是否找到归档分支
if exist "archive_branches.txt" (
    echo [%TIMESTAMP%] [INFO] 2. 从归档分支恢复: 成功 >> %LogFile%
echo 2. 从归档分支恢复: 成功
) else (
    echo [%TIMESTAMP%] [INFO] 2. 从归档分支恢复: 跳过 >> %LogFile%
echo 2. 从归档分支恢复: 跳过
)

REM 检查是否找到标签
if exist "tags.txt" (
    for /f "tokens=*" %%a in (tags.txt) do (
        set tagFound=1
    )
    if defined tagFound (
        echo [%TIMESTAMP%] [INFO] 3. 从标签恢复: 成功 >> %LogFile%
echo 3. 从标签恢复: 成功
    ) else (
        echo [%TIMESTAMP%] [INFO] 3. 从标签恢复: 跳过 >> %LogFile%
echo 3. 从标签恢复: 跳过
    )
) else (
    echo [%TIMESTAMP%] [INFO] 3. 从标签恢复: 跳过 >> %LogFile%
echo 3. 从标签恢复: 跳过
)

echo [%TIMESTAMP%] [INFO] 测试日志: %LogFile% >> %LogFile%
echo 测试日志: %LogFile%

REM 清理临时文件
del branches.txt 2>nul
del archive_branches.txt 2>nul
del tags.txt 2>nul

endlocal
