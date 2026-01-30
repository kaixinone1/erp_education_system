# Git自动备份功能使用指南

## 功能介绍
本功能通过Git版本控制和PowerShell脚本实现系统配置文件和代码的自动备份，确保数据安全和版本追溯。

## 核心组件
1. **.gitignore** - Git忽略规则配置
2. **git_backup.ps1** - 自动备份脚本
3. **Windows任务计划程序** - 定时执行配置

## 初始化步骤

### 1. 初始化Git仓库（已完成）
```bash
git init
```

### 2. 配置Git用户信息（首次使用时）
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 3. 首次提交
```bash
git add .
git commit -m "初始化仓库: 首次提交"
```

## 脚本使用方法

### 基本用法
```powershell
# 基本备份（默认参数）
.it_backup.ps1

# 自定义备份分支
.it_backup.ps1 -BackupBranch "backup_2024"

# 推送到远程仓库
.it_backup.ps1 -PushToRemote
```

### 参数说明
- `-BackupBranch`: 备份分支名称（默认: backup）
- `-MainBranch`: 主分支名称（默认: main）
- `-CommitMessage`: 提交信息（默认: 自动备份 + 时间戳）
- `-PushToRemote`: 是否推送到远程仓库（默认: false）
- `-RemoteName`: 远程仓库名称（默认: origin）
- `-LogFile`: 日志文件路径（默认: backup_log.txt）

## 定时任务配置

### Windows任务计划程序设置步骤
1. 打开**任务计划程序**
2. 点击**创建基本任务**
3. 输入任务名称（如"Git自动备份"）
4. 设置触发器（如每日凌晨2点）
5. 操作选择**启动程序**
6. 程序/脚本：`powershell.exe`
7. 添加参数：`-ExecutionPolicy Bypass -File "D:\erp_thirteen\git_backup.ps1"`
8. 起始于：`D:\erp_thirteen`
9. 完成设置并启用任务

## 远程仓库配置（可选）

### 添加远程仓库
```bash
# 添加GitHub远程仓库
git remote add origin https://github.com/yourusername/erp_thirteen.git

# 首次推送
git push -u origin main
git push origin backup
```

## 备份策略

### 分支管理
- **main**: 主分支，存放核心代码和配置
- **backup**: 备份分支，每日自动备份
- **archive**: 归档分支，定期创建历史版本快照

### 备份频率
- **每日自动备份**: 通过任务计划程序定时执行
- **手动触发备份**: 重要修改后执行脚本
- **远程同步**: 可选配置，定期推送到远程仓库

## 恢复操作

### 从备份分支恢复
```bash
# 查看备份历史
git log --oneline backup

# 恢复到指定版本
git checkout main
git reset --hard <backup_commit_hash>
```

### 从远程仓库恢复
```bash
# 克隆仓库
git clone https://github.com/yourusername/erp_thirteen.git

# 切换到备份分支
git checkout backup
```

## 日志管理
- 备份日志存储在 `backup_log.txt`
- 定期检查日志确保备份正常执行
- 异常情况会在日志中标记为ERROR级别

## 注意事项
1. 首次使用前请确保Git已正确安装
2. 定期检查备份日志，确保备份任务正常执行
3. 重要修改后建议手动执行备份
4. 如有远程仓库，请确保网络连接正常
5. 定期清理旧的备份分支，保持仓库大小合理

## 故障排查
- **Git命令失败**: 检查Git是否正确安装和配置
- **权限问题**: 确保脚本有执行权限
- **远程推送失败**: 检查网络连接和远程仓库权限
- **任务计划程序不执行**: 检查任务配置和系统权限

---

**版本**: 1.0.0
**更新日期**: 2026-01-30
**维护者**: System Administrator