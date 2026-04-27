from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.import_routes import router as import_router
from routes.data_routes import router as data_router
from routes.table_structure_routes import router as table_structure_router
from routes.field_config_routes import router as field_config_router
from routes.admin_routes import router as admin_router
from routes.todo_work_routes import router as todo_work_router
from routes.status_change_routes import router as status_change_router
from routes.template_routes import router as template_router
from routes.retirement_report_routes import router as retirement_report_router
from routes.template_fill_routes import router as template_fill_router
from routes.report_designer_routes import router as report_designer_router
from routes.retirement_data_routes import router as retirement_data_router
from routes.template_field_mapping_routes import router as template_field_mapping_router
from routes.checklist_template_routes import router as checklist_template_router
from routes.intermediate_table_routes import router as intermediate_table_router
from routes.filter_condition_routes import router as filter_condition_router
from routes.migration_routes import router as migration_router
from routes.tag_relations_routes import router as tag_relations_router
from routes.universal_template_routes import router as universal_template_router
from routes.todo_system_routes import router as todo_system_router
from routes.menu_routes_new import router as menu_router
from routes.performance_pay_routes import router as performance_pay_router
from routes.template_import_test import router as template_import_test_router
from routes.aggregate_query_routes import router as aggregate_query_router
import json
import os

app = FastAPI()

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务 - 用于模板文件预览
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "templates_test")
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "uploads", "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)
app.mount("/template-files", StaticFiles(directory=UPLOAD_DIR), name="template-files")
app.mount("/exports", StaticFiles(directory=EXPORT_DIR), name="exports")

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
NAVIGATION_FILE = os.path.join(CONFIG_DIR, 'navigation.json')

def load_navigation_from_file():
    """从文件加载导航配置 - 只保留元模块"""
    try:
        if os.path.exists(NAVIGATION_FILE):
            with open(NAVIGATION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 确保至少包含元模块
                if not data.get('modules') or len(data['modules']) == 0:
                    return get_default_meta_modules()
                return data
    except Exception as e:
        print(f"加载导航配置失败: {e}")
    
    # 首次启动或文件损坏时，返回元模块配置
    return get_default_meta_modules()

def get_default_meta_modules():
    """获取默认元模块配置 - 仅系统管理和模块管理"""
    return {
        "modules": [
            {
                "id": "system",
                "title": "系统管理",
                "icon": "Setting",
                "path": "/system",
                "type": "module",
                "children": [
                    {
                        "id": "system-modules",
                        "title": "模块管理",
                        "icon": "Grid",
                        "path": "/system/module-mgt",
                        "type": "component",
                        "component": "Modules",
                        "api_endpoint": "/api/data/modules"
                    }
                ]
            }
        ]
    }

def save_navigation_to_file(data):
    """保存导航配置到文件"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(NAVIGATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存导航配置失败: {e}")
        return False

# 加载导航数据
NAVIGATION_DATA = load_navigation_from_file()

@app.get("/")
def root():
    return {"message": "Backend is running"}

# 导航API - 使用 navigation.json 文件
@app.get("/api/navigation-admin/tree")
def get_navigation():
    # 每次读取时从文件加载，确保获取最新数据
    return load_navigation_from_file()

@app.put("/api/navigation-admin/tree")
def update_navigation(data: dict):
    global NAVIGATION_DATA
    
    # 更新内存中的数据
    NAVIGATION_DATA = data
    
    # 保存到文件
    if save_navigation_to_file(data):
        return {"status": "success", "message": "导航配置已更新并保存"}
    else:
        return {"status": "error", "message": "导航配置更新失败"}

# 注册路由
app.include_router(import_router)
app.include_router(data_router)
app.include_router(table_structure_router)
app.include_router(field_config_router)
app.include_router(admin_router)
app.include_router(todo_work_router)
app.include_router(status_change_router)
app.include_router(template_router)
app.include_router(retirement_report_router)
app.include_router(template_fill_router)
app.include_router(report_designer_router)
app.include_router(retirement_data_router)
app.include_router(template_field_mapping_router)
app.include_router(checklist_template_router)
app.include_router(intermediate_table_router)
app.include_router(filter_condition_router)
app.include_router(migration_router)
app.include_router(tag_relations_router)
app.include_router(universal_template_router)
app.include_router(todo_system_router)
print("[OK] 待办系统路由已注册")

# 注册退休测算路由
from routes.retirement_routes import router as retirement_router
app.include_router(retirement_router)
print("[OK] 退休测算路由已注册")

# 注册菜单管理路由
app.include_router(menu_router)
print("[OK] 菜单管理路由已注册")

# 注册绩效工资审批路由
app.include_router(performance_pay_router)
print("[OK] 绩效工资审批路由已注册")

# 注册模板导入测试路由
app.include_router(template_import_test_router)
print("[OK] 模板导入测试路由已注册")

# 注册聚合查询路由
app.include_router(aggregate_query_router)
print("[OK] 聚合查询路由已注册")

# 注册通用中间表框架路由（旧框架，保留兼容）
from utils.intermediate_table_framework import register_intermediate_table, create_intermediate_table_routes

# 注册退休呈报数据中间表（旧框架）
try:
    retirement_engine = register_intermediate_table(
        os.path.join(CONFIG_DIR, 'intermediate_tables', 'retirement_report_data.json')
    )
    app.include_router(create_intermediate_table_routes('retirement_report_data'))
    print("[OK] 退休呈报数据中间表已注册到旧框架")
except Exception as e:
    print(f"注册退休呈报数据中间表失败: {e}")

# 注册自动表管理框架（新框架 - 零配置）
from utils.auto_table_framework import create_auto_table_routes, create_dynamic_auto_table_router

# 注册通用动态路由 - 支持任意表名
try:
    app.include_router(create_dynamic_auto_table_router())
    print("[OK] 通用自动表路由已注册（支持任意表名）")
except Exception as e:
    print(f"注册通用自动表路由失败: {e}")

# 注册退休呈报表到新框架（逐步迁移）
try:
    app.include_router(create_auto_table_routes('retirement_report_data'))
    print("[OK] 退休呈报表已注册到新框架")
except Exception as e:
    print(f"注册退休呈报表到新框架失败: {e}")

# 注册中间表管理路由
try:
    from utils.intermediate_table_manager import create_intermediate_table_manager_routes
    app.include_router(create_intermediate_table_manager_routes())
    print("[OK] 中间表管理路由已注册")
except Exception as e:
    print(f"注册中间表管理路由失败: {e}")

@app.post("/api/open-folder")
async def open_folder(data: dict):
    """打开文件夹"""
    try:
        import os
        import subprocess
        
        folder_path = data.get('path', 'D:\\exports')
        
        # 确保文件夹存在
        os.makedirs(folder_path, exist_ok=True)
        
        # 使用Windows资源管理器打开文件夹
        subprocess.Popen(f'explorer "{folder_path}"', shell=True)
        
        return {"status": "success", "message": f"已打开文件夹: {folder_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/select-folder")
async def select_folder(data: dict):
    """弹出文件夹选择对话框"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        import threading
        import queue
        
        result_queue = queue.Queue()
        current_path = data.get('current_path', '')
        
        def show_dialog():
            try:
                # 创建隐藏的根窗口
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                
                # 打开文件夹选择对话框
                selected = filedialog.askdirectory(
                    title='选择保存位置',
                    initialdir=current_path if current_path else 'C:/'
                )
                
                root.destroy()
                result_queue.put(selected)
            except Exception as e:
                result_queue.put('')
        
        # 在新线程中运行对话框
        dialog_thread = threading.Thread(target=show_dialog)
        dialog_thread.start()
        dialog_thread.join(timeout=60)  # 最多等待60秒
        
        if not result_queue.empty():
            selected_path = result_queue.get()
            if selected_path:
                return {"status": "success", "selected_path": selected_path}
        
        return {"status": "cancelled", "message": "用户取消选择"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 启动服务器
if __name__ == "__main__":
    # 启动定时任务
    try:
        from services.scheduler_service import start_scheduler
        start_scheduler()
    except Exception as e:
        print(f"[WARN] 定时任务启动失败: {e}")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
