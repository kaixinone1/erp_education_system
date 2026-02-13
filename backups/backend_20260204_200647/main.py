from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.import_routes import router as import_router
from routes.data_routes import router as data_router
from routes.table_structure_routes import router as table_structure_router
from routes.field_config_routes import router as field_config_router
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
