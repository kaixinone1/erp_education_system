"""
重启后端服务器并清除所有缓存
"""
import os
import sys
import subprocess
import glob
import shutil

print("=== 重启后端服务器 ===\n")

# 1. 删除所有 __pycache__ 目录
print("1. 清除 Python 缓存...")
cache_dirs = glob.glob("**/__pycache__", recursive=True)
for cache_dir in cache_dirs:
    try:
        shutil.rmtree(cache_dir)
        print(f"   删除: {cache_dir}")
    except Exception as e:
        print(f"   跳过: {cache_dir}")

# 2. 删除 .pyc 文件
print("\n2. 清除 .pyc 文件...")
pyc_files = glob.glob("**/*.pyc", recursive=True)
for pyc_file in pyc_files:
    try:
        os.remove(pyc_file)
    except:
        pass

# 3. 删除 pyo 文件
pyo_files = glob.glob("**/*.pyo", recursive=True)
for pyo_file in pyo_files:
    try:
        os.remove(pyo_file)
    except:
        pass

print(f"   已清除 {len(pyc_files)} 个缓存文件")

print("\n3. 缓存清除完成")
print("\n✅ 请手动重启后端服务器:")
print("   1. 在VSCode终端中按 Ctrl+C 停止当前服务器")
print("   2. 重新运行: python -m uvicorn main:app --reload --port 8000")
print("\n   或者在新的终端中运行:")
print("   cd d:\\erp_thirteen\\tp_education_system\\backend")
print("   python -m uvicorn main:app --reload --port 8000")
