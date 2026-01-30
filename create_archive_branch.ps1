#!/usr/bin/env pwsh

# 自动创建归档分支脚本
# 功能：根据版本管理策略创建归档分支并推送到远程仓库

# 设置变量
$ArchiveDate = Get-Date -Format 'yyyy-MM-dd'
$MainBranch = "main"
$RemoteName = "origin"
$CreateTag = $true
$TagName = "v$(Get-Date -Format 'yyyy.MM.dd')"
$TagMessage = "归档版本: $ArchiveDate"
$LogFile = "archive_branch_log.txt"
$ArchiveBranch = "archive/$ArchiveDate"

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

# 开始执行
Write-Log "开始执行归档分支创建"
Write-Log "归档日期: $ArchiveDate"
Write-Log "主分支: $MainBranch"
Write-Log "远程仓库: $RemoteName"
Write-Log "创建标签: $CreateTag"
Write-Log "标签名称: $TagName"
Write-Log "归档分支名称: $ArchiveBranch"

# 检查当前目录是否为Git仓库
if (-not (Test-Path ".git")) {
    Write-Log "错误: 当前目录不是Git仓库" "ERROR"
    exit 1
}

# 切换到主分支
Write-Log "切换到主分支: $MainBranch"
git checkout $MainBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "错误: 切换到主分支失败" "ERROR"
    exit 1
}

# 拉取最新代码
Write-Log "拉取最新代码"
git pull $RemoteName $MainBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "警告: 拉取代码失败，可能是网络问题" "WARNING"
    Write-Log "继续执行归档分支创建" "INFO"
}

# 检查归档分支是否已存在
Write-Log "检查归档分支是否已存在"
$branches = git branch -a
if ($branches -match $ArchiveBranch) {
    Write-Log "警告: 归档分支已存在，将删除并重新创建" "WARNING"
    # 删除本地分支
    git branch -D $ArchiveBranch
    # 删除远程分支（如果存在）
    git push $RemoteName --delete $ArchiveBranch 2>$null
}

# 创建归档分支
Write-Log "创建归档分支: $ArchiveBranch"
git checkout -b $ArchiveBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "错误: 创建归档分支失败" "ERROR"
    exit 1
}

# 推送归档分支到远程仓库
Write-Log "推送归档分支到远程仓库"
git push $RemoteName $ArchiveBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "警告: 推送归档分支失败，可能是网络问题" "WARNING"
    Write-Log "归档分支已在本地创建，但未推送到远程" "INFO"
} else {
    Write-Log "成功: 归档分支已推送到远程仓库" "INFO"
}

# 创建标签
if ($CreateTag) {
    Write-Log "创建版本标签: $TagName"
    git tag -a $TagName -m "$TagMessage"
    if ($LASTEXITCODE -ne 0) {
        Write-Log "警告: 创建标签失败" "WARNING"
    } else {
        Write-Log "推送标签到远程仓库"
        git push $RemoteName $TagName
        if ($LASTEXITCODE -ne 0) {
            Write-Log "警告: 推送标签失败，可能是网络问题" "WARNING"
            Write-Log "标签已在本地创建，但未推送到远程" "INFO"
        } else {
            Write-Log "成功: 标签已推送到远程仓库" "INFO"
        }
    }
}

# 切换回主分支
Write-Log "切换回主分支: $MainBranch"
git checkout $MainBranch
if ($LASTEXITCODE -ne 0) {
    Write-Log "警告: 切换回主分支失败" "WARNING"
}

# 显示分支状态
Write-Log "显示当前分支状态"
git branch

# 生成总结
Write-Log "=== 归档分支创建总结 ==="
Write-Log "归档日期: $ArchiveDate"
Write-Log "归档分支: $ArchiveBranch"
Write-Log "主分支: $MainBranch"
Write-Log "远程仓库: $RemoteName"
Write-Log "创建标签: $CreateTag"
if ($CreateTag) {
    Write-Log "标签名称: $TagName"
}
Write-Log "归档分支创建完成"
Write-Log "日志文件: $LogFile"

# 显示执行结果
Write-Host "=== 归档分支创建完成 ==="
Write-Host "归档分支: $ArchiveBranch"
Write-Host "创建日期: $ArchiveDate"
if ($CreateTag) {
    Write-Host "版本标签: $TagName"
}
Write-Host "详细日志请查看: $LogFile"

exit 0
