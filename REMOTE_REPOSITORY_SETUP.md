# 远程仓库配置指南

## 概述
远程仓库配置是Git自动备份功能的重要组成部分，用于提供异地备份保障。本指南详细说明如何配置远程仓库并集成到自动备份流程中。

## 为什么需要远程仓库
1. **异地备份**：防止本地存储故障导致数据丢失
2. **版本历史**：提供完整的版本历史记录
3. **协作开发**：支持多开发人员协作
4. **灾难恢复**：在本地环境损坏时快速恢复

## 支持的远程仓库服务
- **GitHub**：全球最大的代码托管平台
- **GitLab**：支持私有仓库和CI/CD
- **Gitee**：国内代码托管平台，访问速度快
- **Bitbucket**：支持无限私有仓库

## GitHub配置步骤

### 1. 创建GitHub仓库
1. 登录GitHub账号
2. 点击右上角"+"按钮，选择"New repository"
3. 仓库名称：`erp_thirteen`
4. 描述：`ERP系统自动备份仓库`
5. 仓库类型：选择"Private"（私有）
6. 勾选"Add a README file"（可选）
7. 点击"Create repository"

### 2. 获取仓库URL
创建成功后，复制仓库的HTTPS或SSH URL，格式如下：
- HTTPS: `https://github.com/yourusername/erp_thirteen.git`
- SSH: `git@github.com:yourusername/erp_thirteen.git`

### 3. 配置本地Git远程仓库
```bash
# 添加远程仓库（使用HTTPS URL）
git remote add origin https://github.com/yourusername/erp_thirteen.git

# 验证远程仓库配置
git remote -v

# 首次推送主分支和备份分支
git push -u origin main backup
```

### 4. 配置GitHub认证
#### 方法1：使用GitHub Personal Access Token（推荐）
1. 登录GitHub账号
2. 进入"Settings" > "Developer settings" > "Personal access tokens"
3. 点击"Generate new token"
4. 填写Token名称：`ERP系统备份`
5. 权限选择：
   - `repo`：完整的仓库访问权限
   - `workflow`：工作流权限（可选）
6. 点击"Generate token"
7. 复制生成的Token，保存到安全位置
8. 首次推送时，用户名输入GitHub账号，密码输入Personal Access Token

#### 方法2：使用SSH密钥
1. 生成SSH密钥（如果没有）：
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```
2. 复制公钥（`id_ed25519.pub`）内容
3. 登录GitHub，进入"Settings" > "SSH and GPG keys"
4. 点击"New SSH key"
5. 粘贴公钥内容，点击"Add SSH key"

## GitLab配置步骤

### 1. 创建GitLab仓库
1. 登录GitLab账号
2. 点击"New project"
3. 选择"Create blank project"
4. 项目名称：`erp_thirteen`
5. 可见性级别：选择"Private"
6. 点击"Create project"

### 2. 配置本地Git远程仓库
```bash
# 添加远程仓库
git remote add origin https://gitlab.com/yourusername/erp_thirteen.git

# 首次推送
git push -u origin main backup
```

## Gitee配置步骤

### 1. 创建Gitee仓库
1. 登录Gitee账号
2. 点击右上角"+"按钮，选择"新建仓库"
3. 仓库名称：`erp_thirteen`
4. 仓库介绍：`ERP系统自动备份仓库`
5. 仓库类型：选择"私有"
6. 点击"创建"

### 2. 配置本地Git远程仓库
```bash
# 添加远程仓库
git remote add origin https://gitee.com/yourusername/erp_thirteen.git

# 首次推送
git push -u origin main backup
```

## 修改备份脚本支持远程推送

### 1. 修改PowerShell脚本
编辑 `git_backup.ps1` 文件，确保包含以下功能：

```powershell
# 可选：推送到远程仓库
if ($PushToRemote) {
    try {
        Write-Log "推送到远程仓库: $RemoteName"
        # 推送主分支
        git push $RemoteName $MainBranch
        # 推送备份分支
        git push $RemoteName $BackupBranch
        Write-Log "推送成功"
    } catch {
        Write-Log "推送失败: $($_.Exception.Message)" "ERROR"
        # 推送失败不影响本地备份
    }
}
```

### 2. 修改批处理脚本
编辑 `git_backup.bat` 文件，添加远程推送功能：

```batch
REM 推送到远程仓库
set PUSH_TO_REMOTE=true
if "%PUSH_TO_REMOTE%"=="true" (
    echo [%TIMESTAMP%] [INFO] 推送到远程仓库: origin >> %LOG_FILE%
    echo 推送到远程仓库: origin
    git push origin %MAIN_BRANCH%
    if %errorlevel% neq 0 (
        echo [%TIMESTAMP%] [ERROR] 推送主分支失败 >> %LOG_FILE%
        echo 推送主分支失败
    )
    git push origin %BACKUP_BRANCH%
    if %errorlevel% neq 0 (
        echo [%TIMESTAMP%] [ERROR] 推送备份分支失败 >> %LOG_FILE%
        echo 推送备份分支失败
    )
    echo [%TIMESTAMP%] [INFO] 推送完成 >> %LOG_FILE%
    echo 推送完成
)
```

## 配置自动推送

### PowerShell脚本参数
```powershell
# 启用远程推送
.git_backup.ps1 -PushToRemote

# 自定义远程仓库名称
.git_backup.ps1 -PushToRemote -RemoteName "github"
```

### 批处理脚本配置
编辑 `git_backup.bat` 文件，修改 `PUSH_TO_REMOTE` 变量：

```batch
set PUSH_TO_REMOTE=true
```

## 定时任务配置

### Windows任务计划程序设置
1. 打开**任务计划程序**
2. 点击**创建基本任务**
3. 输入任务名称：`Git自动备份（含远程推送）`
4. 设置触发器（如每日凌晨2点）
5. 操作选择**启动程序**
6. 程序/脚本：`powershell.exe`
7. 添加参数：`-ExecutionPolicy Bypass -File "D:\erp_thirteen\git_backup.ps1" -PushToRemote`
8. 起始于：`D:\erp_thirteen`
9. 完成设置并启用任务

## 验证远程仓库配置

### 检查远程仓库连接
```bash
# 检查远程仓库状态
git remote show origin

# 获取远程仓库信息
git fetch origin

# 比较本地和远程分支
git log --oneline main origin/main
```

### 测试完整备份流程
1. 修改本地文件（如README.md）
2. 运行备份脚本：`.git_backup.ps1 -PushToRemote`
3. 登录远程仓库网站，验证文件是否已更新
4. 检查备份分支是否同步

## 常见问题解决

### 1. 推送失败：认证错误
**原因**：Git认证失败
**解决方法**：
- 确保使用正确的Personal Access Token
- 检查SSH密钥配置
- 尝试重新输入凭证

### 2. 推送失败：网络连接错误
**原因**：网络连接不稳定
**解决方法**：
- 检查网络连接
- 尝试使用SSH协议
- 配置Git代理（如果需要）

### 3. 推送失败：分支冲突
**原因**：远程分支与本地分支存在冲突
**解决方法**：
```bash
# 拉取远程更新并合并
git pull origin main --rebase
# 重新推送
git push origin main backup
```

### 4. 仓库容量限制
**原因**：远程仓库存储容量不足
**解决方法**：
- 清理不必要的大文件
- 使用Git LFS（Large File Storage）
- 升级仓库存储方案

## 安全注意事项

1. **保护认证信息**：不要在脚本中硬编码Personal Access Token
2. **使用HTTPS或SSH**：优先使用SSH协议，更安全
3. **定期更新凭证**：定期更新Personal Access Token
4. **限制仓库访问**：设置合适的仓库访问权限
5. **敏感信息过滤**：确保不会将敏感信息推送到远程仓库

## 最佳实践

1. **定期检查**：每周检查远程仓库同步状态
2. **分支管理**：保持主分支和备份分支的同步
3. **标签管理**：对重要版本创建标签
4. **备份策略**：结合本地备份和远程备份
5. **文档更新**：及时更新配置文档

## 紧急恢复流程

### 从远程仓库恢复
1. 克隆远程仓库：
   ```bash
   git clone https://github.com/yourusername/erp_thirteen.git
   ```
2. 切换到主分支：
   ```bash
   git checkout main
   ```
3. 恢复备份分支：
   ```bash
   git checkout backup
   ```

### 从特定版本恢复
1. 查看版本历史：
   ```bash
   git log --oneline
   ```
2. 恢复到特定版本：
   ```bash
   git checkout main
   git reset --hard <commit_hash>
   ```

---

**版本**：1.0.0
**更新日期**：2026-01-30
**维护者**：System Administrator