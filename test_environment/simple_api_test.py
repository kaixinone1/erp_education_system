#!/usr/bin/env python3
"""简单API测试 - 模拟浏览器调用"""
import urllib.request
import urllib.parse

template_id = "职工退休申报表html"

print("=" * 70)
print("API测试 - 模拟浏览器调用")
print("=" * 70)

for teacher_id in [273, 299]:
    print(f"\n测试教师ID: {teacher_id}")
    print("-" * 70)
    
    encoded_template_id = urllib.parse.quote(template_id)
    url = f"http://localhost:8000/api/template-field-mapping/preview/{encoded_template_id}?teacher_id={teacher_id}&mode=fill"
    
    print(f"URL: {url}")
    
    # 创建请求（模拟浏览器）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            # 查找姓名
            if '王军峰' in html:
                name = '王军峰'
            elif '王德' in html:
                name = '王德'
            else:
                name = '未找到'
            
            # 查找{{姓名}}
            import re
            remaining = len(re.findall(r'\{\{\s*姓名\s*\}\}', html))
            
            print(f"返回HTML长度: {len(html)}")
            print(f"找到的姓名: {name}")
            print(f"剩余{{姓名}}占位符: {remaining} 个")
            
            # 显示HTML中姓名的上下文
            if name != '未找到':
                idx = html.find(name)
                if idx > 0:
                    context = html[max(0, idx-50):idx+50]
                    print(f"上下文: ...{context}...")
            
    except Exception as e:
        print(f"错误: {e}")

print("\n" + "=" * 70)
