@echo off

REM 设置字符编码为UTF-8
chcp 65001 >nul

REM 开发日志管理脚本
REM 功能：自动跟踪开发步骤，详细记录开发过程，生成开发日志

setlocal enabledelayedexpansion

REM 配置变量
set LOG_DIR=dev_logs
set MAIN_LOG_FILE=%LOG_DIR%\dev_main.log
set DAILY_LOG_FILE=%LOG_DIR%\dev_%date:~0,4%%date:~5,2%%date:~8,2%.log
set TEMPLATE_FILE=%LOG_DIR%\log_template.txt
set CONFIG_FILE=%LOG_DIR%\config.txt

REM 生成时间戳
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set current_date=%%c-%%a-%%b)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set current_time=%%a:%%b)
set TIMESTAMP=%current_date% %current_time%

REM 创建日志目录
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
    echo 创建日志目录: %LOG_DIR%
)

REM 创建配置文件
if not exist "%CONFIG_FILE%" (
    echo [CONFIG] > "%CONFIG_FILE%"
    echo PROJECT_NAME=ERP系统 >> "%CONFIG_FILE%"
    echo DEVELOPER=System Administrator >> "%CONFIG_FILE%"
    echo LOG_LEVEL=INFO >> "%CONFIG_FILE%"
    echo AUTO_TRACK=true >> "%CONFIG_FILE%"
    echo TEMPLATE_ENABLED=true >> "%CONFIG_FILE%"
    echo 配置文件创建完成: %CONFIG_FILE%
)

REM 创建日志模板
if not exist "%TEMPLATE_FILE%" (
    echo # 开发日志模板 > "%TEMPLATE_FILE%"
    echo ## 基本信息 >> "%TEMPLATE_FILE%"
    echo - 日期: {DATE} >> "%TEMPLATE_FILE%"
    echo - 时间: {TIME} >> "%TEMPLATE_FILE%"
    echo - 开发者: {DEVELOPER} >> "%TEMPLATE_FILE%"
    echo - 项目: {PROJECT_NAME} >> "%TEMPLATE_FILE%"
    echo - 阶段: {PHASE} >> "%TEMPLATE_FILE%"
    echo >> "%TEMPLATE_FILE%"
    echo ## 开发内容 >> "%TEMPLATE_FILE%"
    echo - 任务描述: {TASK} >> "%TEMPLATE_FILE%"
    echo - 完成情况: {STATUS} >> "%TEMPLATE_FILE%"
    echo - 使用工具: {TOOLS} >> "%TEMPLATE_FILE%"
    echo - 相关文件: {FILES} >> "%TEMPLATE_FILE%"
    echo >> "%TEMPLATE_FILE%"
    echo ## 技术细节 >> "%TEMPLATE_FILE%"
    echo - 实现方法: {METHOD} >> "%TEMPLATE_FILE%"
    echo - 遇到问题: {ISSUES} >> "%TEMPLATE_FILE%"
    echo - 解决方案: {SOLUTIONS} >> "%TEMPLATE_FILE%"
    echo - 代码变更: {CODE_CHANGES} >> "%TEMPLATE_FILE%"
    echo >> "%TEMPLATE_FILE%"
    echo ## 测试结果 >> "%TEMPLATE_FILE%"
    echo - 测试状态: {TEST_STATUS} >> "%TEMPLATE_FILE%"
    echo - 测试方法: {TEST_METHOD} >> "%TEMPLATE_FILE%"
    echo - 测试结果: {TEST_RESULTS} >> "%TEMPLATE_FILE%"
    echo - 问题修复: {BUG_FIXES} >> "%TEMPLATE_FILE%"
    echo >> "%TEMPLATE_FILE%"
    echo ## 后续计划 >> "%TEMPLATE_FILE%"
    echo - 下一步任务: {NEXT_TASKS} >> "%TEMPLATE_FILE%"
    echo - 预计时间: {ESTIMATED_TIME} >> "%TEMPLATE_FILE%"
    echo - 依赖项: {DEPENDENCIES} >> "%TEMPLATE_FILE%"
    echo >> "%TEMPLATE_FILE%"
    echo ## 备注 >> "%TEMPLATE_FILE%"
    echo {NOTES} >> "%TEMPLATE_FILE%"
    echo 日志模板创建完成: %TEMPLATE_FILE%
)

REM 日志函数
echo [%TIMESTAMP%] [INFO] 开发日志管理脚本启动 >> "%MAIN_LOG_FILE%"
echo 开发日志管理脚本启动

echo 选择操作：
echo 1. 开始新的开发任务
echo 2. 记录开发步骤
echo 3. 完成开发任务
echo 4. 查看开发日志
echo 5. 导出开发日志
echo 6. 配置管理
echo 7. 退出

echo.
set /p choice=请输入选择（1-7）：

echo.

if "%choice%"=="1" goto :start_task
if "%choice%"=="2" goto :record_step
if "%choice%"=="3" goto :complete_task
if "%choice%"=="4" goto :view_logs
if "%choice%"=="5" goto :export_logs
if "%choice%"=="6" goto :config
if "%choice%"=="7" goto :exit

:start_task
    echo [%TIMESTAMP%] [INFO] 开始新的开发任务 >> "%MAIN_LOG_FILE%"
    echo 开始新的开发任务
    
    set /p task_name=请输入任务名称：
    set /p task_desc=请输入任务描述：
    set /p task_phase=请输入开发阶段（需求/设计/实现/测试/部署）：
    set /p task_est_time=请输入预计完成时间：
    
    set TASK_ID=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%
    set TASK_LOG_FILE=%LOG_DIR%\task_%TASK_ID%.log
    
    echo [%TIMESTAMP%] [INFO] 任务ID: %TASK_ID% >> "%MAIN_LOG_FILE%"
    echo [%TIMESTAMP%] [INFO] 任务名称: %task_name% >> "%MAIN_LOG_FILE%"
    
    REM 创建任务日志文件
    echo # 开发任务日志 > "%TASK_LOG_FILE%"
    echo ## 任务信息 >> "%TASK_LOG_FILE%"
    echo - 任务ID: %TASK_ID% >> "%TASK_LOG_FILE%"
    echo - 任务名称: %task_name% >> "%TASK_LOG_FILE%"
    echo - 任务描述: %task_desc% >> "%TASK_LOG_FILE%"
    echo - 开发阶段: %task_phase% >> "%TASK_LOG_FILE%"
    echo - 开始时间: %TIMESTAMP% >> "%TASK_LOG_FILE%"
    echo - 预计完成时间: %task_est_time% >> "%TASK_LOG_FILE%"
    echo - 开发者: System Administrator >> "%TASK_LOG_FILE%"
    echo. >> "%TASK_LOG_FILE%"
    echo ## 开发步骤 >> "%TASK_LOG_FILE%"
    
    echo [%TIMESTAMP%] [INFO] 任务日志创建完成: %TASK_LOG_FILE% >> "%MAIN_LOG_FILE%"
    echo 任务日志创建完成: %TASK_LOG_FILE%
    echo 任务ID: %TASK_ID%
    
    REM 记录到每日日志
    echo [%TIMESTAMP%] [START] 任务: %task_name% (ID: %TASK_ID%) >> "%DAILY_LOG_FILE%"
    echo [%TIMESTAMP%] [START] 描述: %task_desc% >> "%DAILY_LOG_FILE%"
    echo [%TIMESTAMP%] [START] 阶段: %task_phase% >> "%DAILY_LOG_FILE%"
    
    goto :menu

:record_step
    echo [%TIMESTAMP%] [INFO] 记录开发步骤 >> "%MAIN_LOG_FILE%"
    echo 记录开发步骤
    
    set /p task_id=请输入任务ID：
    set /p step_desc=请输入步骤描述：
    set /p step_details=请输入详细内容：
    set /p step_tools=请输入使用的工具：
    set /p step_files=请输入相关文件：
    
    set STEP_ID=step_%time:~0,2%%time:~3,2%%time:~6,2%
    set TASK_LOG_FILE=%LOG_DIR%\task_%task_id%.log
    
    if exist "%TASK_LOG_FILE%" (
        echo. >> "%TASK_LOG_FILE%"
        echo ### 步骤: %STEP_ID% >> "%TASK_LOG_FILE%"
        echo - 时间: %TIMESTAMP% >> "%TASK_LOG_FILE%"
        echo - 描述: %step_desc% >> "%TASK_LOG_FILE%"
        echo - 详细内容: %step_details% >> "%TASK_LOG_FILE%"
        echo - 使用工具: %step_tools% >> "%TASK_LOG_FILE%"
        echo - 相关文件: %step_files% >> "%TASK_LOG_FILE%"
        
        echo [%TIMESTAMP%] [STEP] 任务ID: %task_id%, 步骤: %step_desc% >> "%DAILY_LOG_FILE%"
        echo [%TIMESTAMP%] [INFO] 步骤记录完成: %STEP_ID% >> "%MAIN_LOG_FILE%"
        echo 步骤记录完成: %STEP_ID%
    ) else (
        echo 错误: 任务日志文件不存在: %TASK_LOG_FILE%
        echo [%TIMESTAMP%] [ERROR] 任务日志文件不存在: %TASK_LOG_FILE% >> "%MAIN_LOG_FILE%"
    )
    
    goto :menu

:complete_task
    echo [%TIMESTAMP%] [INFO] 完成开发任务 >> "%MAIN_LOG_FILE%"
    echo 完成开发任务
    
    set /p task_id=请输入任务ID：
    set /p task_status=请输入任务状态（成功/部分成功/失败）：
    set /p task_results=请输入完成结果：
    set /p task_issues=请输入遇到的问题：
    set /p task_solutions=请输入解决方案：
    set /p task_next=请输入下一步计划：
    
    set TASK_LOG_FILE=%LOG_DIR%\task_%task_id%.log
    
    if exist "%TASK_LOG_FILE%" (
        echo. >> "%TASK_LOG_FILE%"
        echo ## 任务完成信息 >> "%TASK_LOG_FILE%"
        echo - 完成时间: %TIMESTAMP% >> "%TASK_LOG_FILE%"
        echo - 任务状态: %task_status% >> "%TASK_LOG_FILE%"
        echo - 完成结果: %task_results% >> "%TASK_LOG_FILE%"
        echo - 遇到的问题: %task_issues% >> "%TASK_LOG_FILE%"
        echo - 解决方案: %task_solutions% >> "%TASK_LOG_FILE%"
        echo - 下一步计划: %task_next% >> "%TASK_LOG_FILE%"
        
        echo [%TIMESTAMP%] [COMPLETE] 任务ID: %task_id%, 状态: %task_status% >> "%DAILY_LOG_FILE%"
        echo [%TIMESTAMP%] [INFO] 任务完成记录: %task_id% >> "%MAIN_LOG_FILE%"
        echo 任务完成记录: %task_id%
    ) else (
        echo 错误: 任务日志文件不存在: %TASK_LOG_FILE%
        echo [%TIMESTAMP%] [ERROR] 任务日志文件不存在: %TASK_LOG_FILE% >> "%MAIN_LOG_FILE%"
    )
    
    goto :menu

:view_logs
    echo [%TIMESTAMP%] [INFO] 查看开发日志 >> "%MAIN_LOG_FILE%"
    echo 查看开发日志
    
    echo 选择日志类型：
    echo 1. 主日志文件
    echo 2. 每日日志文件
    echo 3. 任务日志文件
    echo 4. 返回
    
    set /p log_choice=请输入选择（1-4）：
    
    if "%log_choice%"=="1" (
        if exist "%MAIN_LOG_FILE%" (
            echo 查看主日志文件: %MAIN_LOG_FILE%
            type "%MAIN_LOG_FILE%"
        ) else (
            echo 主日志文件不存在: %MAIN_LOG_FILE%
        )
    ) else if "%log_choice%"=="2" (
        if exist "%DAILY_LOG_FILE%" (
            echo 查看每日日志文件: %DAILY_LOG_FILE%
            type "%DAILY_LOG_FILE%"
        ) else (
            echo 每日日志文件不存在: %DAILY_LOG_FILE%
        )
    ) else if "%log_choice%"=="3" (
        set /p view_task_id=请输入任务ID：
        set view_task_file=%LOG_DIR%\task_%view_task_id%.log
        if exist "%view_task_file%" (
            echo 查看任务日志文件: %view_task_file%
            type "%view_task_file%"
        ) else (
            echo 任务日志文件不存在: %view_task_file%
        )
    ) else if "%log_choice%"=="4" (
        goto :menu
    )
    
    pause
    goto :menu

:export_logs
    echo [%TIMESTAMP%] [INFO] 导出开发日志 >> "%MAIN_LOG_FILE%"
    echo 导出开发日志
    
    set /p export_format=请选择导出格式（txt/md）：
    set export_file=%LOG_DIR%\export_%date:~0,4%%date:~5,2%%date:~8,2%.%export_format%
    
    echo 导出日志到: %export_file%
    
    if "%export_format%"=="txt" (
        echo # 开发日志导出 > "%export_file%"
        echo - 导出时间: %TIMESTAMP% >> "%export_file%"
        echo - 项目: ERP系统 >> "%export_file%"
        echo. >> "%export_file%"
        echo ## 主日志内容 >> "%export_file%"
        if exist "%MAIN_LOG_FILE%" (
            type "%MAIN_LOG_FILE%" >> "%export_file%"
        )
        echo. >> "%export_file%"
        echo ## 每日日志内容 >> "%export_file%"
        if exist "%DAILY_LOG_FILE%" (
            type "%DAILY_LOG_FILE%" >> "%export_file%"
        )
    ) else if "%export_format%"=="md" (
        echo # 开发日志导出 > "%export_file%"
        echo ## 导出信息 >> "%export_file%"
        echo - 导出时间: %TIMESTAMP% >> "%export_file%"
        echo - 项目: ERP系统 >> "%export_file%"
        echo - 开发者: System Administrator >> "%export_file%"
        echo. >> "%export_file%"
        echo ## 主日志内容 >> "%export_file%"
        echo ``` >> "%export_file%"
        if exist "%MAIN_LOG_FILE%" (
            type "%MAIN_LOG_FILE%" >> "%export_file%"
        )
        echo ``` >> "%export_file%"
        echo. >> "%export_file%"
        echo ## 每日日志内容 >> "%export_file%"
        echo ``` >> "%export_file%"
        if exist "%DAILY_LOG_FILE%" (
            type "%DAILY_LOG_FILE%" >> "%export_file%"
        )
        echo ``` >> "%export_file%"
    )
    
    echo [%TIMESTAMP%] [INFO] 日志导出完成: %export_file% >> "%MAIN_LOG_FILE%"
    echo 日志导出完成: %export_file%
    
    goto :menu

:config
    echo [%TIMESTAMP%] [INFO] 配置管理 >> "%MAIN_LOG_FILE%"
    echo 配置管理
    
    echo 当前配置：
    if exist "%CONFIG_FILE%" (
        type "%CONFIG_FILE%"
    ) else (
        echo 配置文件不存在
    )
    
    echo.
    echo 1. 修改项目名称
    echo 2. 修改开发者
    echo 3. 修改日志级别
    echo 4. 启用/禁用自动跟踪
    echo 5. 返回
    
    set /p config_choice=请输入选择（1-5）：
    
    if "%config_choice%"=="1" (
        set /p new_project=请输入新项目名称：
        if exist "%CONFIG_FILE%" (
            for /f "usebackq delims=" %%a in ("%CONFIG_FILE%") do (
                set line=%%a
                if "!line:~0,13!"=="PROJECT_NAME=" (
                    echo PROJECT_NAME=%new_project% >> "%CONFIG_FILE%.tmp"
                ) else (
                    echo !line! >> "%CONFIG_FILE%.tmp"
                )
            )
            move "%CONFIG_FILE%.tmp" "%CONFIG_FILE%" >nul
            echo 项目名称已修改为: %new_project%
        )
    ) else if "%config_choice%"=="2" (
        set /p new_developer=请输入新开发者名称：
        if exist "%CONFIG_FILE%" (
            for /f "usebackq delims=" %%a in ("%CONFIG_FILE%") do (
                set line=%%a
                if "!line:~0,11!"=="DEVELOPER=" (
                    echo DEVELOPER=%new_developer% >> "%CONFIG_FILE%.tmp"
                ) else (
                    echo !line! >> "%CONFIG_FILE%.tmp"
                )
            )
            move "%CONFIG_FILE%.tmp" "%CONFIG_FILE%" >nul
            echo 开发者已修改为: %new_developer%
        )
    ) else if "%config_choice%"=="3" (
        set /p new_level=请输入新日志级别（INFO/WARNING/ERROR）：
        if exist "%CONFIG_FILE%" (
            for /f "usebackq delims=" %%a in ("%CONFIG_FILE%") do (
                set line=%%a
                if "!line:~0,9!"=="LOG_LEVEL=" (
                    echo LOG_LEVEL=%new_level% >> "%CONFIG_FILE%.tmp"
                ) else (
                    echo !line! >> "%CONFIG_FILE%.tmp"
                )
            )
            move "%CONFIG_FILE%.tmp" "%CONFIG_FILE%" >nul
            echo 日志级别已修改为: %new_level%
        )
    ) else if "%config_choice%"=="4" (
        set /p auto_track=请输入是否启用自动跟踪（true/false）：
        if exist "%CONFIG_FILE%" (
            for /f "usebackq delims=" %%a in ("%CONFIG_FILE%") do (
                set line=%%a
                if "!line:~0,11!"=="AUTO_TRACK=" (
                    echo AUTO_TRACK=%auto_track% >> "%CONFIG_FILE%.tmp"
                ) else (
                    echo !line! >> "%CONFIG_FILE%.tmp"
                )
            )
            move "%CONFIG_FILE%.tmp" "%CONFIG_FILE%" >nul
            echo 自动跟踪已设置为: %auto_track%
        )
    ) else if "%config_choice%"=="5" (
        goto :menu
    )
    
    goto :menu

:menu
    echo.
    echo 1. 开始新的开发任务
    echo 2. 记录开发步骤
    echo 3. 完成开发任务
    echo 4. 查看开发日志
    echo 5. 导出开发日志
    echo 6. 配置管理
    echo 7. 退出
    
    set /p choice=请输入选择（1-7）：
    
    if "%choice%"=="1" goto :start_task
    if "%choice%"=="2" goto :record_step
    if "%choice%"=="3" goto :complete_task
    if "%choice%"=="4" goto :view_logs
    if "%choice%"=="5" goto :export_logs
    if "%choice%"=="6" goto :config
    if "%choice%"=="7" goto :exit
    
    goto :menu

:exit
    echo [%TIMESTAMP%] [INFO] 开发日志管理脚本退出 >> "%MAIN_LOG_FILE%"
    echo 开发日志管理脚本退出
    
    endlocal
    exit /b 0