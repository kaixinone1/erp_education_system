@echo off

REM 修复中文乱码问题的脚本
REM 功能：设置正确的字符编码，解决批处理文件中的中文乱码

setlocal

REM 设置字符编码为UTF-8
chcp 65001 >nul

REM 生成时间戳
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set current_date=%%c-%%a-%%b)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set current_time=%%a:%%b)
set TIMESTAMP=%current_date% %current_time%

echo [%TIMESTAMP%] 开始修复中文乱码问题
echo [%TIMESTAMP%] 当前字符编码: UTF-8

REM 1. 修改现有批处理文件，添加编码设置
echo [%TIMESTAMP%] 1. 修改现有批处理文件

REM 修改git_backup.bat
if exist "git_backup.bat" (
    echo [%TIMESTAMP%] 修改 git_backup.bat
    REM 备份原文件
    copy "git_backup.bat" "git_backup.bat.bak" >nul
    REM 读取原文件内容
    set "content="
    for /f "usebackq delims=" %%a in ("git_backup.bat") do (
        set "content=!content!%%a\n"
    )
    REM 在文件开头添加编码设置
    set "new_content=@echo off\n\nREM 设置字符编码为UTF-8\nchcp 65001 >nul\n\n!content!"
    REM 写回文件
    echo !new_content! > "git_backup.bat"
    echo [%TIMESTAMP%] git_backup.bat 修改完成
)

REM 修改create_archive_branch.bat
if exist "create_archive_branch.bat" (
    echo [%TIMESTAMP%] 修改 create_archive_branch.bat
    copy "create_archive_branch.bat" "create_archive_branch.bat.bak" >nul
    set "content="
    for /f "usebackq delims=" %%a in ("create_archive_branch.bat") do (
        set "content=!content!%%a\n"
    )
    set "new_content=@echo off\n\nREM 设置字符编码为UTF-8\nchcp 65001 >nul\n\n!content!"
    echo !new_content! > "create_archive_branch.bat"
    echo [%TIMESTAMP%] create_archive_branch.bat 修改完成
)

REM 修改backup_monitor.bat
if exist "backup_monitor.bat" (
    echo [%TIMESTAMP%] 修改 backup_monitor.bat
    copy "backup_monitor.bat" "backup_monitor.bat.bak" >nul
    set "content="
    for /f "usebackq delims=" %%a in ("backup_monitor.bat") do (
        set "content=!content!%%a\n"
    )
    set "new_content=@echo off\n\nREM 设置字符编码为UTF-8\nchcp 65001 >nul\n\n!content!"
    echo !new_content! > "backup_monitor.bat"
    echo [%TIMESTAMP%] backup_monitor.bat 修改完成
)

REM 修改test_backup_restore.bat
if exist "test_backup_restore.bat" (
    echo [%TIMESTAMP%] 修改 test_backup_restore.bat
    copy "test_backup_restore.bat" "test_backup_restore.bat.bak" >nul
    set "content="
    for /f "usebackq delims=" %%a in ("test_backup_restore.bat") do (
        set "content=!content!%%a\n"
    )
    set "new_content=@echo off\n\nREM 设置字符编码为UTF-8\nchcp 65001 >nul\n\n!content!"
    echo !new_content! > "test_backup_restore.bat"
    echo [%TIMESTAMP%] test_backup_restore.bat 修改完成
)

REM 2. 创建编码测试脚本
echo [%TIMESTAMP%] 2. 创建编码测试脚本

REM 创建编码测试脚本
echo @echo off > test_encoding.bat
echo. >> test_encoding.bat
echo REM 编码测试脚本 >> test_encoding.bat
echo REM 功能：测试中文显示是否正常 >> test_encoding.bat
echo. >> test_encoding.bat
echo REM 设置字符编码为UTF-8 >> test_encoding.bat
echo chcp 65001 >nul >> test_encoding.bat
echo. >> test_encoding.bat
echo echo 测试中文显示：你好，世界！ >> test_encoding.bat
echo echo 当前日期：^%date^% >> test_encoding.bat
echo echo 当前时间：^%time^% >> test_encoding.bat
echo echo 编码测试完成 >> test_encoding.bat
echo. >> test_encoding.bat
echo pause >> test_encoding.bat

echo [%TIMESTAMP%] 编码测试脚本创建完成

REM 3. 显示修复完成信息
echo [%TIMESTAMP%] 3. 修复完成

echo. 
echo ===============================
echo 中文乱码修复完成
echo ===============================
echo 已完成以下操作：
echo 1. 修改了所有批处理文件，添加了UTF-8编码设置
echo 2. 创建了编码测试脚本 test_encoding.bat
echo 3. 备份了原始批处理文件（.bak后缀）
echo.
echo 请运行 test_encoding.bat 测试中文显示是否正常
echo ===============================

endlocal
