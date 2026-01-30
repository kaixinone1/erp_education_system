#!/usr/bin/env pwsh

# Git自动备份脚本
# 功能：自动执行Git备份操作，包括添加、提交、分支管理和远程推送

param(
    [string]$BackupBranch = "backup",
    [string]$MainBranch = "main",
    [string]$CommitMessage = "自动备份: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    [switch]$PushToRemote = $true,
    [string]$RemoteName = "origin",
    [string]$LogFile = "backup_log.txt"
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

Write-Log "开始执行Git自动备份"
Write-Log "备份分支: $BackupBranch"
Write-Log "主分支: $MainBranch"
Write-Log "远程推送: $PushToRemote"
Write-Log "远程仓库: $RemoteName"

# 检查当前目录是否为Git仓库
if (-not (Test-Path ".git")) {
    Write-Log "错误: 当前目录不是Git仓库" "ERROR"
    exit 1
}

# 检查Git状态
Write-Log "检查Git状态"
try {
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Log "发现修改的文件，开始添加和提交"
        git add .
        git commit -m "$CommitMessage"
        Write-Log "提交成功"
    } else {
        Write-Log "没有发现修改的文件，跳过提交"
    }
} catch {
    Write-Log "Git操作失败: $($_.Exception.Message)" "ERROR"
    exit 1
}

# 检查并创建备份分支
Write-Log "检查并创建备份分支"
try {
    $allBranches = git branch
    $branchExists = $false
    foreach ($branch in $allBranches) {
        if ($branch -match $BackupBranch) {
            $branchExists = $true
            break
        }
    }
    
    if (-not $branchExists) {
        Write-Log "创建备份分支: $BackupBranch"
        git branch $BackupBranch
    } else {
        Write-Log "备份分支已存在: $BackupBranch"
    }
    
    Write-Log "切换到备份分支"
    git checkout $BackupBranch
    
    Write-Log "合并主分支到备份分支"
    git merge $MainBranch --no-ff -m "合并主分支到备份分支: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    
    Write-Log "切换回主分支"
    git checkout $MainBranch
} catch {
    Write-Log "分支操作失败: $($_.Exception.Message)" "ERROR"
    exit 1
}

# 推送到远程仓库
if ($PushToRemote) {
    Write-Log "推送到远程仓库: $RemoteName"
    try {
        # 检查远程仓库是否存在
        $remotes = git remote -v
        if (-not $remotes) {
            Write-Log "警告: 远程仓库未配置，跳过推送" "WARNING"
        } else {
            # 推送主分支
            Write-Log "推送主分支: $MainBranch"
            git push $RemoteName $MainBranch
            
            # 推送备份分支
            Write-Log "推送备份分支: $BackupBranch"
            git push $RemoteName $BackupBranch
            
            Write-Log "远程推送成功"
        }
    } catch {
        Write-Log "远程推送失败: $($_.Exception.Message)" "ERROR"
        # 推送失败不影响本地备份
    }
}

Write-Log "Git自动备份执行完成"
Write-Log "======================================"
