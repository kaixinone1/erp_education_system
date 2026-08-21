"""
通用项目启动器 - 双击启动前后端服务器
支持任意 backend/ + frontend/ 结构的项目
"""
import os
import sys
import subprocess
import time
import socket
import json
import logging
import shutil
from pathlib import Path

# ================ 配置 ================
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
BROWSER_URL = f"http://localhost:{FRONTEND_PORT}"
STARTUP_TIMEOUT = 60  # 最多等60秒
LOG_FILE = ".startup.log"

# 静默模式，不弹控制台窗口
CREATE_NO_WINDOW = 0x08000000

# ================ 日志 ================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger("startup")

def log(msg: str):
    """同时输出到日志文件"""
    logger.info(msg)
    print(f"[启动器] {msg}")

# ================ 工具函数 ================

def find_executable(names: list) -> str | None:
    """查找可执行文件"""
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def is_port_ready(port: int) -> bool:
    """检查端口是否就绪"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False


def wait_for_port(port: int, timeout: int = STARTUP_TIMEOUT) -> bool:
    """等待端口就绪"""
    log(f"等待端口 {port} 就绪...")
    waited = 0
    while waited < timeout:
        if is_port_ready(port):
            log(f"端口 {port} 已就绪 (耗时 {waited}秒)")
            return True
        time.sleep(1)
        waited += 1
    log(f"端口 {port} 超时未就绪 ({timeout}秒)")
    return False


def kill_port(port: int):
    """杀掉占用端口的进程"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr ":{port} " | findstr "LISTENING"',
            shell=True, capture_output=True, text=True,
            creationflags=CREATE_NO_WINDOW
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    subprocess.run(
                        f'taskkill /F /PID {pid}',
                        shell=True, capture_output=True,
                        creationflags=CREATE_NO_WINDOW
                    )
                    log(f"已释放端口 {port} (PID={pid})")
            time.sleep(1)
    except Exception as e:
        log(f"释放端口 {port} 失败: {e}")


# ================ 项目检测 ================

def detect_project(root: Path) -> dict:
    """自动检测项目结构，返回 {backend_dir, frontend_dir, backend_entry, frontend_entry}"""
    result = {
        "backend_dir": None,
        "frontend_dir": None,
        "backend_entry": None,  # main.py 路径
        "frontend_entry": None,  # package.json 路径
    }
    
    # 策略1: 直接子目录 backend/ + frontend/
    for subdir in root.iterdir():
        if subdir.is_dir():
            if subdir.name.lower() in ('backend', 'server', 'api'):
                if (subdir / 'main.py').exists():
                    result["backend_dir"] = subdir
                    result["backend_entry"] = subdir / 'main.py'
            if subdir.name.lower() in ('frontend', 'web', 'client', 'ui'):
                if (subdir / 'package.json').exists():
                    result["frontend_dir"] = subdir
                    result["frontend_entry"] = subdir / 'package.json'
    
    # 策略2: 递归2层查找
    if not result["backend_dir"] or not result["frontend_dir"]:
        for subdir in root.iterdir():
            if subdir.is_dir():
                for subsubdir in subdir.iterdir():
                    if subsubdir.is_dir():
                        if not result["backend_dir"] and subsubdir.name.lower() in ('backend', 'server', 'api'):
                            if (subsubdir / 'main.py').exists():
                                result["backend_dir"] = subsubdir
                                result["backend_entry"] = subsubdir / 'main.py'
                        if not result["frontend_dir"] and subsubdir.name.lower() in ('frontend', 'web', 'client', 'ui'):
                            if (subsubdir / 'package.json').exists():
                                result["frontend_dir"] = subsubdir
                                result["frontend_entry"] = subsubdir / 'package.json'
    
    # 策略3: 当前目录
    if not result["backend_entry"] and (root / 'main.py').exists():
        result["backend_dir"] = root
        result["backend_entry"] = root / 'main.py'
    if not result["frontend_entry"] and (root / 'package.json').exists():
        result["frontend_dir"] = root
        result["frontend_entry"] = root / 'package.json'
    
    return result


# ================ 后端启动 ================

def start_backend(backend_dir: Path) -> subprocess.Popen | None:
    """启动后端服务器"""
    try:
        # 检测 Python
        python = find_executable(['python', 'python3'])
        if not python:
            log("错误: 未找到 Python，请安装 Python 3.8+")
            return None
        
        main_file = backend_dir / 'main.py'
        if not main_file.exists():
            log(f"错误: 未找到 {main_file}")
            return None
        
        # 检测虚拟环境
        venv_python = None
        for venv_name in ['venv', '.venv', 'env', '.env']:
            venv_dir = backend_dir / venv_name
            if venv_dir.exists():
                venv_python_dir = venv_dir / 'Scripts' if os.name == 'nt' else venv_dir / 'bin'
                if venv_python_dir.exists():
                    venv_python_path = venv_python_dir / 'python.exe' if os.name == 'nt' else venv_python_dir / 'python'
                    if venv_python_path.exists():
                        venv_python = str(venv_python_path)
                        break
        
        if venv_python:
            python = venv_python
            log(f"使用虚拟环境: {venv_python}")
        else:
            # 检查是否有 requirements.txt，自动安装依赖
            req_file = backend_dir / 'requirements.txt'
            if req_file.exists():
                # 检查是否有虚拟环境或全局已安装 uvicorn
                try:
                    subprocess.run(
                        [python, '-c', 'import uvicorn'],
                        capture_output=True, creationflags=CREATE_NO_WINDOW
                    )
                except:
                    log("正在安装后端依赖...")
                    # 创建虚拟环境
                    if not (backend_dir / 'venv').exists():
                        subprocess.run(
                            [python, '-m', 'venv', 'venv'],
                            cwd=str(backend_dir), capture_output=True,
                            creationflags=CREATE_NO_WINDOW
                        )
                    venv_python = str(backend_dir / 'venv' / 'Scripts' / 'python.exe')
                    subprocess.run(
                        [venv_python, '-m', 'pip', 'install', '-r', 'requirements.txt', '-q'],
                        cwd=str(backend_dir), capture_output=True,
                        creationflags=CREATE_NO_WINDOW
                    )
                    python = venv_python
                    log("后端依赖安装完成")

        # 释放端口
        if is_port_ready(BACKEND_PORT):
            log(f"端口 {BACKEND_PORT} 被占用，尝试释放...")
            kill_port(BACKEND_PORT)
        
        # 启动后端
        cmd = [python, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', str(BACKEND_PORT)]
        log(f"启动后端: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            cwd=str(backend_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW
        )
        
        return process
    
    except Exception as e:
        log(f"后端启动失败: {e}")
        return None


# ================ 前端启动 ================

def start_frontend(frontend_dir: Path) -> subprocess.Popen | None:
    """启动前端服务器"""
    try:
        # 检测 Node.js
        node = find_executable(['node'])
        if not node:
            log("错误: 未找到 Node.js，请安装 Node.js 16+")
            return None
        
        npm = find_executable(['npm.cmd', 'npm'])
        if not npm:
            log("错误: 未找到 npm")
            return None
        
        package_json = frontend_dir / 'package.json'
        if not package_json.exists():
            log(f"错误: 未找到 {package_json}")
            return None
        
        # 检查 node_modules
        if not (frontend_dir / 'node_modules').exists():
            log("正在安装前端依赖 (npm install)...")
            subprocess.run(
                [npm, 'install'],
                cwd=str(frontend_dir), capture_output=True,
                creationflags=CREATE_NO_WINDOW
            )
            log("前端依赖安装完成")
        
        # 读取 package.json 确定启动命令
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
            scripts = pkg.get('scripts', {})
            
            # 优先使用 dev，否则用 start
            if 'dev' in scripts:
                script_name = 'dev'
            elif 'start' in scripts:
                script_name = 'start'
            elif 'serve' in scripts:
                script_name = 'serve'
            else:
                script_name = 'dev'  # 兜底
        except:
            script_name = 'dev'
        
        # 释放端口
        if is_port_ready(FRONTEND_PORT):
            log(f"端口 {FRONTEND_PORT} 被占用，尝试释放...")
            kill_port(FRONTEND_PORT)
        
        # 启动前端
        cmd = [npm, 'run', script_name, '--', '--port', str(FRONTEND_PORT), '--host', '0.0.0.0']
        log(f"启动前端: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            cwd=str(frontend_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW
        )
        
        return process
    
    except Exception as e:
        log(f"前端启动失败: {e}")
        return None


# ================ 主流程 ================

def main():
    root = Path(os.getcwd())
    log(f"项目目录: {root}")
    log(f"{'='*50}")
    
    # 检测项目结构
    project = detect_project(root)
    
    if not project["backend_entry"]:
        log("错误: 未检测到后端项目 (main.py)")
        log(f"已扫描目录: {root}")
        for d in root.iterdir():
            if d.is_dir():
                log(f"  - {d.name}/")
        input("\n按 Enter 退出...")
        return
    
    if not project["frontend_entry"]:
        log("错误: 未检测到前端项目 (package.json)")
        log(f"已扫描目录: {root}")
        for d in root.iterdir():
            if d.is_dir():
                log(f"  - {d.name}/")
        input("\n按 Enter 退出...")
        return
    
    log(f"后端: {project['backend_dir']}")
    log(f"前端: {project['frontend_dir']}")
    
    # 启动后端
    backend_proc = start_backend(project["backend_dir"])
    if not backend_proc:
        log("后端启动失败，请检查 .startup.log")
        input("\n按 Enter 退出...")
        return
    
    # 启动前端
    frontend_proc = start_frontend(project["frontend_dir"])
    if not frontend_proc:
        log("前端启动失败，请检查 .startup.log")
        # 清理后端
        backend_proc.terminate()
        input("\n按 Enter 退出...")
        return
    
    # 等待端口就绪
    backend_ready = wait_for_port(BACKEND_PORT)
    frontend_ready = wait_for_port(FRONTEND_PORT)
    
    if backend_ready and frontend_ready:
        log("=" * 50)
        log(f"启动成功！")
        log(f"后端: http://localhost:{BACKEND_PORT}")
        log(f"前端: http://localhost:{FRONTEND_PORT}")
        log(f"日志: {LOG_FILE}")
        log("=" * 50)
        
        # 自动打开浏览器
        time.sleep(1)
        try:
            os.startfile(BROWSER_URL)
            log(f"浏览器已打开: {BROWSER_URL}")
        except Exception as e:
            log(f"无法打开浏览器: {e}")
        
        # 退出，让服务器继续运行
        sys.exit(0)
    else:
        log("启动失败！")
        if not backend_ready:
            log(f"后端端口 {BACKEND_PORT} 未就绪")
        if not frontend_ready:
            log(f"前端端口 {FRONTEND_PORT} 未就绪")
        
        # 清理
        backend_proc.terminate()
        frontend_proc.terminate()
        input("\n按 Enter 退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()