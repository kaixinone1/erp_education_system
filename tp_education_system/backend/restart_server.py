"""
重启后端服务器并清除缓存
"""
import os
import sys
import subprocess
import glob

print("=== 重启后端服务器 ===")

# 1. 删除所有 __pycache__ 目录
print("\n1. 清除 Python 缓存...")
cache_dirs = glob.glob("**/__pycache__", recursive=True)
for cache_dir in cache_dirs:
    try:
        import shutil
        shutil.rmtree(cache_dir)
        print(f"   删除: {cache_dir}")
    except Exception as e:
        print(f"   跳过: {cache_dir} ({e})")

# 2. 删除 .pyc 文件
print("\n2. 清除 .pyc 文件...")
pyc_files = glob.glob("**/*.pyc", recursive=True)
for pyc_file in pyc_files:
    try:
        os.remove(pyc_file)
        print(f"   删除: {pyc_file}")
    except Exception as e:
        pass

# 3. 删除 pyo 文件
pyo_files = glob.glob("**/*.pyo", recursive=True)
for pyo_file in pyo_files:
    try:
        os.remove(pyo_file)
    except:
        pass

print("\n3. 缓存清除完成")
print("\n✅ 请手动重启后端服务器:")
print("   方法1: 在VSCode中按 Ctrl+C 停止，然后重新运行")
print("   方法2: 直接运行: python -m uvicorn main:app --reload --port 8000")
