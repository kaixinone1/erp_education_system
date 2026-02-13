#!/usr/bin/env python3
"""测试智能填充API"""
import requests

def test():
    try:
        # 测试智能填充下载API
        url = 'http://localhost:8000/api/templates/2/smart-fill-download?teacher_id=273'
        print(f"请求URL: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功！正在保存文件...")
            with open('test_filled_report.docx', 'wb') as f:
                f.write(response.content)
            print("文件已保存: test_filled_report.docx")
        else:
            print(f"失败: {response.text}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test()
