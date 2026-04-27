#!/usr/bin/env python3
"""
重新加载模块并测试
"""
import sys
import importlib

# 清除缓存
if 'routes.todo_system_routes' in sys.modules:
    del sys.modules['routes.todo_system_routes']

# 重新导入
from routes.todo_system_routes import get_todo_list
import asyncio

# 测试运行
async def test():
    try:
        result = await get_todo_list()
        data = result.get('data', [])
        print(f"返回数据条数: {len(data)}")
        print("\n前3条数据:")
        for i, item in enumerate(data[:3], 1):
            print(f"\n{i}. ID: {item.get('id')}")
            print(f"   teacher_name: {item.get('teacher_name')}")
            print(f"   business_type: {item.get('business_type')}")
            print(f"   business_type_display: {item.get('business_type_display')}")
            print(f"   template_name: {item.get('template_name')}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
