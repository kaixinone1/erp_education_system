#!/usr/bin/env python3
"""
测试导入页面 - 模拟浏览器访问
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_import_page():
    """测试导入页面"""
    
    # 启动浏览器
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 访问首页
        print("=" * 80)
        print("访问首页")
        print("=" * 80)
        driver.get("http://localhost:5173/")
        time.sleep(2)
        
        # 获取页面标题
        print(f"页面标题: {driver.title}")
        
        # 获取控制台日志
        logs = driver.get_log('browser')
        if logs:
            print("\n浏览器控制台日志:")
            for log in logs:
                print(f"  [{log['level']}] {log['message']}")
        
        # 访问导入页面
        print("\n" + "=" * 80)
        print("访问导入页面")
        print("=" * 80)
        driver.get("http://localhost:5173/import/workbench")
        time.sleep(3)
        
        # 获取页面源代码
        page_source = driver.page_source
        print(f"页面内容长度: {len(page_source)}")
        
        # 检查是否包含关键内容
        if "数据导入工作台" in page_source:
            print("✅ 页面包含'数据导入工作台'")
        else:
            print("❌ 页面不包含'数据导入工作台'")
            print("\n页面内容前1000字符:")
            print(page_source[:1000])
        
        # 获取控制台日志
        logs = driver.get_log('browser')
        if logs:
            print("\n浏览器控制台日志:")
            for log in logs:
                print(f"  [{log['level']}] {log['message']}")
        else:
            print("\n✅ 没有浏览器控制台错误")
        
        # 检查是否有错误元素
        error_elements = driver.find_elements(By.CLASS_NAME, "error")
        if error_elements:
            print(f"\n发现 {len(error_elements)} 个错误元素")
            for elem in error_elements:
                print(f"  错误: {elem.text}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_import_page()
