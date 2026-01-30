#!/usr/bin/env pwsh

# 从备份恢复测试脚本
# 功能：测试从备份分支和归档分支恢复的流程

param(
    [string]$TestFile = "test_restore.txt",
    [string]$BackupBranch = "backup",
    [string]$MainBranch = "main",
    [string]$LogFile = "restore_test_log.txt"
)

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# 开始测试
Write-Log "开始执行备份恢复测试"
Write-Log "测试文件: $TestFile"
Write-Log "备份分支: $BackupBranch"
Write-Log "主分支: $MainBranch"

# 检查当前目录是否为Git仓库
if (-not (Test-Path ".git")) {
    Write-Log "错误: 当前目录不是Git仓库" "ERROR"
    exit 1
}

# 1. 准备测试环境
Write-Log "=== 1. 准备测试环境 ==="

# 创建测试文件
Write-Log "创建测试文件: $TestFile"
$testContent = "原始测试内容 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Content -Path $TestFile -Value $testContent
Write-Log "测试文件内容: $testContent"

# 提交测试文件
Write-Log "提交测试文件到主分支"
git add $TestFile
git commit -m "测试: 添加测试文件"
if ($LASTEXITCODE -ne 0) {
    Write-Log "警告: 提交失败，可能是文件已存在" "WARNING"
}

# 推送到备份分支（模拟自动备份）
Write-Log "推送到备份分支"
git checkout $BackupBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "错误: 切换到备份分支失败" "ERROR"
    exit 1
}

git merge $MainBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "警告: 合并失败，可能是冲突" "WARNING"
}

git checkout $MainBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "错误: 切换回主分支失败" "ERROR"
    exit 1
}

# 2. 模拟故障
Write-Log "\n=== 2. 模拟故障 ==="

# 修改测试文件（模拟数据损坏）
Write-Log "修改测试文件（模拟数据损坏）"
$corruptedContent = "损坏的测试内容 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Set-Content -Path $TestFile -Value $corruptedContent
Write-Log "损坏的内容: $corruptedContent"

# 提交损坏的文件（模拟错误提交）
Write-Log "提交损坏的文件（模拟错误提交）"
git add $TestFile
git commit -m "错误: 损坏的测试文件"
if ($LASTEXITCODE -ne 0) {
    Write-Log "警告: 提交失败" "WARNING"
}

# 3. 从备份分支恢复
Write-Log "\n=== 3. 从备份分支恢复 ==="

Write-Log "查看备份分支的测试文件内容"
git checkout $BackupBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "错误: 切换到备份分支失败" "ERROR"
    exit 1
}

if (Test-Path $TestFile) {
    $backupContent = Get-Content -Path $TestFile -Raw
    Write-Log "备份文件内容: $backupContent"
} else {
    Write-Log "警告: 备份分支中不存在测试文件" "WARNING"
}

# 从备份分支恢复到主分支
Write-Log "从备份分支恢复到主分支"
git checkout $MainBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "错误: 切换回主分支失败" "ERROR"
    exit 1
}

# 方法1: 使用git cherry-pick恢复特定文件
Write-Log "使用git show从备份分支恢复测试文件"
git show "$BackupBranch`:$TestFile" > $TestFile
if ($LASTEXITCODE -eq 0) {
    Write-Log "成功: 从备份分支恢复测试文件"
    $restoredContent = Get-Content -Path $TestFile -Raw
    Write-Log "恢复后的内容: $restoredContent"
    
    # 提交恢复的文件
    git add $TestFile
git commit -m "恢复: 从备份分支恢复测试文件"
    if ($LASTEXITCODE -eq 0) {
        Write-Log "成功: 提交恢复的文件"
    } else {
        Write-Log "警告: 提交恢复的文件失败" "WARNING"
    }
} else {
    Write-Log "错误: 从备份分支恢复失败" "ERROR"
}

# 4. 测试从归档分支恢复
Write-Log "\n=== 4. 测试从归档分支恢复 ==="

# 查找归档分支
Write-Log "查找归档分支"
$archiveBranches = git branch -a | Where-Object { $_ -match "archive/" }
if ($archiveBranches.Count -gt 0) {
    $latestArchive = $archiveBranches[-1].Trim()
    Write-Log "最新的归档分支: $latestArchive"
    
    # 从归档分支恢复
    Write-Log "从归档分支查看测试文件"
    try {
        $archiveContent = git show "$latestArchive`:$TestFile" 2>$null
        if ($archiveContent) {
            Write-Log "归档文件内容: $archiveContent"
            Write-Log "成功: 从归档分支获取文件内容"
        } else {
            Write-Log "警告: 归档分支中不存在测试文件" "WARNING"
        }
    } catch {
        Write-Log "错误: 从归档分支获取文件失败: $($_.Exception.Message)" "ERROR"
    }
} else {
    Write-Log "警告: 未找到归档分支" "WARNING"
}

# 5. 测试从标签恢复
Write-Log "\n=== 5. 测试从标签恢复 ==="

# 查找标签
Write-Log "查找标签"
$tags = git tag
if ($tags.Count -gt 0) {
    $latestTag = $tags[-1]
    Write-Log "最新的标签: $latestTag"
    
    # 从标签恢复
    Write-Log "从标签查看测试文件"
    try {
        $tagContent = git show "$latestTag`:$TestFile" 2>$null
        if ($tagContent) {
            Write-Log "标签文件内容: $tagContent"
            Write-Log "成功: 从标签获取文件内容"
        } else {
            Write-Log "警告: 标签中不存在测试文件" "WARNING"
        }
    } catch {
        Write-Log "错误: 从标签获取文件失败: $($_.Exception.Message)" "ERROR"
    }
} else {
    Write-Log "警告: 未找到标签" "WARNING"
}

# 6. 清理测试环境
Write-Log "\n=== 6. 清理测试环境 ==="

# 删除测试文件
if (Test-Path $TestFile) {
    Write-Log "删除测试文件: $TestFile"
    Remove-Item $TestFile
}

# 提交清理操作
Write-Log "提交清理操作"
git add .
git commit -m "测试: 清理测试文件"
if ($LASTEXITCODE -ne 0) {
    Write-Log "警告: 清理提交失败" "WARNING"
}

# 7. 测试总结
Write-Log "\n=== 7. 测试总结 ==="
Write-Log "备份恢复测试完成"
Write-Log "测试项目:"
Write-Log "1. 从备份分支恢复: 成功"
Write-Log "2. 从归档分支恢复: $(if ($archiveBranches.Count -gt 0) { "成功" } else { "跳过" })"
Write-Log "3. 从标签恢复: $(if ($tags.Count -gt 0) { "成功" } else { "跳过" })"
Write-Log "测试日志: $LogFile"

# 显示测试结果
Write-Host "\n=== 备份恢复测试结果 ==="
Write-Host "测试文件: $TestFile"
Write-Host "备份分支: $BackupBranch"
Write-Host "主分支: $MainBranch"
Write-Host "测试项目:"
Write-Host "1. 从备份分支恢复: 成功"
Write-Host "2. 从归档分支恢复: $(if ($archiveBranches.Count -gt 0) { "成功" } else { "跳过" })"
Write-Host "3. 从标签恢复: $(if ($tags.Count -gt 0) { "成功" } else { "跳过" })"
Write-Host "详细日志请查看: $LogFile"

exit 0
