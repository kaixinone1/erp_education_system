# 远程仓库配置详细指南

## 概述
本指南详细说明如何为ERP系统配置远程Git仓库，提供异地备份保障。

## 选择远程仓库服务

### 推荐选项
1. **GitHub**：全球最大的代码托管平台，提供免费私有仓库
2. **GitLab**：支持更丰富的CI/CD功能，完全免费的私有仓库
3. **Gitee**：国内平台，访问速度快，适合国内团队

## GitHub配置步骤

### 1. 创建GitHub仓库
1. 登录GitHub账号
2. 点击右上角"+"按钮，选择"New repository"
3. 填写仓库信息：
   - 仓库名称：`erp_thirteen`
   - 描述：`ERP系统自动备份仓库`
   - 仓库类型：`Private`（私有）
   - 勾选：`Add a README file`（可选）
4. 点击"Create repository"

### 2. 获取仓库URL
创建成功后，复制仓库的HTTPS URL，格式如下：
```
https://github.com/yourusername/erp_thirteen.git
```

### 3. 配置本地Git远程仓库
```bash
# 添加远程仓库
git remote add origin https://github.com/yourusername/erp_thirteen.git

# 验证远程仓库配置
git remote -v

# 首次推送所有分支
git push -u origin main backup
```

### 4. 配置GitHub认证
#### 方法1：使用Personal Access Token（推荐）
1. 登录GitHub账号
2. 进入"Settings" > "Developer settings" > "Personal access tokens"
3. 点击"Generate new token"
4. 填写Token信息：
   - 名称：`ERP系统备份`
   - 权限：勾选`repo`（完整的仓库访问权限）
   - 过期时间：选择"No expiration"
5. 点击"Generate token"
6. 复制生成的Token并保存到安全位置
7. 首次推送时，使用Token作为密码

#### 方法2：使用SSH密钥
1. 生成SSH密钥（如果没有）：
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```
2. 复制公钥内容：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
3. 登录GitHub，进入"Settings" > "SSH and GPG keys"
4. 点击"New SSH key"
5. 粘贴公钥内容，点击"Add SSH key"

## GitLab配置步骤

### 1. 创建GitLab仓库
1. 登录GitLab账号
2. 点击"New project"
3. 选择"Create blank project"
4. 填写项目信息：
   - 项目名称：`erp_thirteen`
   - 可见性级别：`Private`
5. 点击"Create project"

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
3. 填写仓库信息：
   - 仓库名称：`erp_thirteen`
   - 仓库介绍：`ERP系统自动备份仓库`
   - 仓库类型：`私有`
4. 点击"创建"

### 2. 配置本地Git远程仓库
```bash
# 添加远程仓库
git remote add origin https://gitee.com/yourusername/erp_thirteen.git

# 首次推送
git push -u origin main backup
```

## 验证远程仓库配置

### 检查远程仓库连接
```bash
# 检查远程仓库配置
git remote -v

# 测试连接
git remote show origin

# 获取远程仓库信息
git fetch origin
```

### 验证推送功能
1. 修改本地文件（如README.md）
2. 运行备份脚本：`.git_backup.ps1`
3. 登录远程仓库网站，验证文件是否已更新
4. 检查备份分支是否同步

## 故障排除

### 推送失败：认证错误
**解决方法**：
- 确保使用正确的Personal Access Token
- 检查SSH密钥配置是否正确
- 尝试重新输入凭证

### 推送失败：网络连接错误
**解决方法**：
- 检查网络连接
- 尝试使用SSH协议
- 配置Git代理（如果需要）

### 推送失败：分支冲突
**解决方法**：
```bash
# 拉取远程更新并合并
git pull origin main --rebase
# 重新推送
git push origin main backup
```

## 安全最佳实践

1. **保护认证信息**：不要在脚本中硬编码Personal Access Token
2. **使用HTTPS或SSH**：优先使用SSH协议，更安全
3. **定期更新凭证**：每3-6个月更新一次Personal Access Token
4. **限制仓库访问**：只邀请必要的团队成员
5. **启用双因素认证**：为GitHub/GitLab/Gitee账号启用2FA

## 配置示例

### GitHub配置示例
```bash
# 添加GitHub远程仓库
git remote add origin https://github.com/erp-system/erp_thirteen.git

# 首次推送
git push -u origin main backup

# 验证配置
git remote -v
# 预期输出：
# origin  https://github.com/erp-system/erp_thirteen.git (fetch)
# origin  https://github.com/erp-system/erp_thirteen.git (push)
```

### SSH配置示例
```bash
# 添加SSH远程仓库
git remote add origin git@github.com:erp-system/erp_thirteen.git

# 首次推送
git push -u origin main backup
```

## 后续操作

配置完成后，备份脚本将自动：
1. 执行本地备份操作
2. 推送到配置的远程仓库
3. 记录详细的执行日志

定期检查远程仓库同步状态，确保备份正常运行。

---

**版本**：1.0.0
**更新日期**：2026-01-30
**维护者**：System Administrator