import sys
import os

# 清除所有缓存模块
modules_to_clear = [key for key in sys.modules.keys() if 'routes' in key or 'main' in key]
for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]

# 设置工作目录
os.chdir(r'd:\erp_thirteen\tp_education_system\backend')
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

# 重新导入并启动
import uvicorn
from main import app

print("=== 服务器重新启动 ===")
print("已清除模块缓存")
uvicorn.run(app, host='0.0.0.0', port=8001)
