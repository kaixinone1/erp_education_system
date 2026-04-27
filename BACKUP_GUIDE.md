# ERP教育系统备份脚本

## 本地备份

项目代码已使用Git进行版本控制，提交记录如下：

```
commit c8e418e
feat: 退休提醒优化和新功能
- 退休提醒增加历史记录检查，避免重复提醒
- 使用新退休政策计算公式
- 新增退休测算功能（按旧/新标准测算）
- 优化待办工作排序（待处理在前）
- 优化办理详情显示（任务项完成情况、办理记录）
- 修复日期选择器时区问题（日期偏移一天）
- 字典表关联获取单位名称和个人身份
```

## Git 远程仓库配置

由于网络原因无法直接访问GitHub，请按以下步骤手动配置：

### 方法一：使用GitHub网页（推荐）

1. 打开浏览器访问：https://github.com/new
2. 登录账号（kaixinone1）
3. 创建一个新仓库，例如：`erp_education_system`
4. **不要勾选** "Add a README file"
5. 创建后，复制仓库地址（例如：`https://github.com/kaixinone1/erp_education_system.git`）
6. 告诉我仓库地址，我帮您配置并推送

### 方法二：使用TortoiseGit（图形界面）

1. 下载安装 TortoiseGit：https://tortoisegit.org/
2. 在项目目录右键 → TortoiseGit → Settings → Git
3. 配置用户名和邮箱
4. 在项目目录右键 → TortoiseGit → Remote → Add
5. 输入名称 `origin` 和仓库地址

### 方法三：使用VS Code

1. 打开VS Code
2. 安装Git扩展
3. 点击左侧源代码管理图标
4. 点击"发布到GitHub"

---

## 数据库备份

如需备份数据库，可运行：

```bash
cd d:\erp_thirteen\tp_education_system\backend
python -c "
import psycopg2
from datetime import datetime
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
# 导出SQL文件（请根据需要修改）
"
```
