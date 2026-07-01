"""
============================================================
服务器自检守护脚本 (Server Watchdog)
============================================================
功能：
- 每30秒通过HTTP请求检测前端(5173)和后端(8000)服务是否可用
- 如果发现服务不可用，自动重启之
- 记录日志到 watchdog.log
- 前后端独立检测和重启，互不影响

用法：
    python watchdog.py

注意：
- 本脚本不使用--reload，由watchdog负责检测和重启
- 使用HTTP健康检查而非端口检测，避免误判
============================================================
"""
import socket
import subprocess
import time
import sys
import os
import urllib.request
from datetime import datetime

FRONTEND_PORT = 5173
BACKEND_PORT = 8000
CHECK_INTERVAL = 30

FRONTEND_URL = f'http://localhost:{FRONTEND_PORT}/'
BACKEND_URL = f'http://localhost:{BACKEND_PORT}/api/dashboard/stats'

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'tp_education_system', 'frontend')
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'tp_education_system', 'backend')

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'watchdog.log')

frontend_process = None
backend_process = None
frontend_failures = 0
backend_failures = 0
MAX_FAILURES = 5


def log(msg: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except:
        pass


def http_check(url: str, timeout: int = 5) -> bool:
    """通过HTTP请求检查服务是否可用"""
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.status == 200
    except:
        return False


def kill_port(port: int):
    """杀掉占用端口的进程"""
    try:
        subprocess.run(
            f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"',
            capture_output=True, shell=True, timeout=15
        )
    except:
        pass


def start_frontend():
    global frontend_process, frontend_failures
    log(f"[前端] 正在启动 (端口 {FRONTEND_PORT})...")
    kill_port(FRONTEND_PORT)
    time.sleep(3)

    try:
        frontend_process = subprocess.Popen(
            'npm run dev -- --host 0.0.0.0',
            cwd=FRONTEND_DIR,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        log(f"[前端] 已启动 (PID: {frontend_process.pid})，等待就绪...")
        time.sleep(5)

        if http_check(FRONTEND_URL, timeout=10):
            log(f"[前端] 启动成功，服务可用")
            frontend_failures = 0
            return True
        else:
            log(f"[前端] 启动后HTTP检查失败，将在下一周期重试")
            frontend_failures += 1
            return False
    except Exception as e:
        log(f"[前端] 启动异常: {e}")
        frontend_failures += 1
        return False


def start_backend():
    global backend_process, backend_failures
    log(f"[后端] 正在启动 (端口 {BACKEND_PORT})...")
    kill_port(BACKEND_PORT)
    time.sleep(3)

    try:
        backend_process = subprocess.Popen(
            f'"{sys.executable}" -m uvicorn main:app --host 0.0.0.0 --port {BACKEND_PORT} --reload',
            cwd=BACKEND_DIR,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        log(f"[后端] 已启动 (PID: {backend_process.pid})，等待就绪...")
        time.sleep(8)

        if http_check(BACKEND_URL, timeout=15):
            log(f"[后端] 启动成功，服务可用")
            backend_failures = 0
            return True
        else:
            log(f"[后端] 启动后HTTP检查失败，将在下一周期重试")
            backend_failures += 1
            return False
    except Exception as e:
        log(f"[后端] 启动异常: {e}")
        backend_failures += 1
        return False


def main():
    global frontend_failures, backend_failures

    log("=" * 60)
    log("服务器自检守护脚本启动 (HTTP健康检查模式)")
    log(f"前端: {FRONTEND_URL}")
    log(f"后端: {BACKEND_URL}")
    log(f"检查间隔: {CHECK_INTERVAL} 秒")
    log("=" * 60)

    while True:
        try:
            frontend_ok = http_check(FRONTEND_URL)
            backend_ok = http_check(BACKEND_URL)

            if not frontend_ok:
                if frontend_failures < MAX_FAILURES:
                    log(f"[前端] 无响应，尝试重启 (失败计数: {frontend_failures})")
                    start_frontend()
                else:
                    log(f"[前端] 连续失败{frontend_failures}次，暂停120秒后重试")
                    time.sleep(120)
                    frontend_failures = 0

            if not backend_ok:
                if backend_failures < MAX_FAILURES:
                    log(f"[后端] 无响应，尝试重启 (失败计数: {backend_failures})")
                    start_backend()
                else:
                    log(f"[后端] 连续失败{backend_failures}次，暂停120秒后重试")
                    time.sleep(120)
                    backend_failures = 0

            if frontend_ok and backend_ok:
                pass

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log("收到退出信号，守护脚本退出")
            break
        except Exception as e:
            log(f"守护脚本异常: {e}")
            time.sleep(60)


if __name__ == '__main__':
    main()