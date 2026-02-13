#!/usr/bin/env pwsh

# 恢复备份脚本
# 功能：从备份恢复代码、数据库、配置文件

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupPath,
    [string]$TargetDir = "D:\erp_thirteen",
    [switch]$Force = $false
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
}

# 检查备份路径
if (-not (Test-Path $BackupPath)) {
    Write-Log "错误: 备份路径不存在: $BackupPath" "ERROR"
    exit 1
}

# 读取备份信息
$backupInfoFile = Join-Path $BackupPath "backup_info.json"
if (Test-Path $backupInfoFile) {
    $backupInfo = Get-Content $backupInfoFile | ConvertFrom-Json
    Write-Log "备份时间: $($backupInfo.backup_time)"
    Write-Log "Git分支: $($backupInfo.git_branch)"
    Write-Log "Git提交: $($backupInfo.git_commit)"
}

# 确认恢复
if (-not $Force) {
    $confirm = Read-Host "确定要从备份恢复吗？这将覆盖现有数据！(yes/no)"
    if ($confirm -ne "yes") {
        Write-Log "恢复已取消"
        exit 0
    }
}

Write-Log "开始恢复备份"
Write-Log "备份路径: $BackupPath"
Write-Log "目标路径: $TargetDir"

# 1. 恢复代码
$codeBackupPath = Join-Path $BackupPath "code"
if (Test-Path $codeBackupPath) {
    Write-Log "开始恢复代码..."
    try {
        # 如果存在Git bundle，优先使用
        $bundleFile = Join-Path $codeBackupPath "repository.bundle"
        if (Test-Path $bundleFile) {
            Write-Log "从Git bundle恢复..."
            # 创建临时目录恢复
            $tempDir = Join-Path $env:TEMP "erp_restore_$(Get-Random)"
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
            git clone $bundleFile $tempDir 2>&1 | Out-Null
            
            # 复制到目标目录
            if (Test-Path $TargetDir) {
                Remove-Item -Path $TargetDir -Recurse -Force
            }
            Copy-Item -Path $tempDir -Destination $TargetDir -Recurse -Force
            Remove-Item -Path $tempDir -Recurse -Force
            Write-Log "代码从Git bundle恢复完成"
        } else {
            # 从项目备份恢复
            $projectBackupPath = Join-Path $codeBackupPath "project"
            if (Test-Path $projectBackupPath) {
                Write-Log "从项目备份恢复..."
                if (Test-Path $TargetDir) {
                    Remove-Item -Path $TargetDir -Recurse -Force
                }
                Copy-Item -Path $projectBackupPath -Destination $TargetDir -Recurse -Force
                Write-Log "代码从项目备份恢复完成"
            }
        }
    } catch {
        Write-Log "代码恢复失败: $($_.Exception.Message)" "ERROR"
    }
}

# 2. 恢复数据库
$dbBackupPath = Join-Path $BackupPath "database"
if (Test-Path $dbBackupPath) {
    Write-Log "开始恢复数据库..."
    try {
        $dbFile = Join-Path $dbBackupPath "taiping_education.sql"
        if (Test-Path $dbFile) {
            # 先删除现有数据库
            $env:PGPASSWORD = "taiping_password"
            & psql -h localhost -U taiping_user -d postgres -c "DROP DATABASE IF EXISTS taiping_education;" 2>&1
            & psql -h localhost -U taiping_user -d postgres -c "CREATE DATABASE taiping_education;" 2>&1
            
            # 恢复数据库
            & psql -h localhost -U taiping_user -d taiping_education -f $dbFile 2>&1
            Write-Log "数据库恢复完成"
        } else {
            Write-Log "数据库备份文件不存在" "WARNING"
        }
    } catch {
        Write-Log "数据库恢复失败: $($_.Exception.Message)" "ERROR"
    }
}

# 3. 恢复配置文件
$configBackupPath = Join-Path $BackupPath "configs"
if (Test-Path $configBackupPath) {
    Write-Log "开始恢复配置文件..."
    try {
        # 恢复后端配置
        $backendConfigSource = Join-Path $configBackupPath "config"
        $backendConfigTarget = Join-Path $TargetDir "tp_education_system\backend\config"
        if (Test-Path $backendConfigSource) {
            if (Test-Path $backendConfigTarget) {
                Remove-Item -Path $backendConfigTarget -Recurse -Force
            }
            Copy-Item -Path $backendConfigSource -Destination $backendConfigTarget -Recurse -Force
        }
        
        # 恢复前端配置
        $frontendConfigSource = Join-Path $configBackupPath "config"
        $frontendConfigTarget = Join-Path $TargetDir "tp_education_system\frontend\src\config"
        if (Test-Path $frontendConfigSource -and -not (Test-Path $frontendConfigTarget)) {
            Copy-Item -Path $frontendConfigSource -Destination $frontendConfigTarget -Recurse -Force
        }
        
        # 恢复环境变量文件
        $envFiles = @(
            @(".env", "tp_education_system\backend\.env"),
            @(".env", "tp_education_system\frontend\.env")
        )
        foreach ($envFile in $envFiles) {
            $sourceFile = Join-Path $configBackupPath $envFile[0]
            $targetFile = Join-Path $TargetDir $envFile[1]
            if (Test-Path $sourceFile) {
                Copy-Item -Path $sourceFile -Destination $targetFile -Force
            }
        }
        
        Write-Log "配置文件恢复完成"
    } catch {
        Write-Log "配置文件恢复失败: $($_.Exception.Message)" "ERROR"
    }
}

Write-Log "备份恢复完成"
Write-Log "请检查恢复后的系统是否正常运行"
Write-Log "======================================"

exit 0
