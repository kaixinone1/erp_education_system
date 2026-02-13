#!/usr/bin/env python3
"""测试预览API - 预览模式"""
import urllib.request
import urllib.parse

template_id = "职工退休申报表html"
teacher_id = 0  # 预览模式
mode = "preview"

encoded_template_id = urllib.parse.quote(template_id)
url = f"http://localhost:8000/api/template-field-mapping/preview/{encoded_template_id}?teacher_id={teacher_id}&mode={mode}"

print(f"请求URL: {url}")
print("=" * 70)

try:
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')
        
        print(f"返回HTML长度: {len(html)}")
        print(f"\n前500字符:")
        print(html[:500])
        
        # 检查是否有内容
        if len(html) < 100:
            print("\n✗ HTML内容太短，可能有问题")
        else:
            print(f"\n✓ HTML内容正常，长度: {len(html)}")
            
        # 保存到文件
        with open('d:/erp_thirteen/preview_test.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\nHTML已保存到: d:/erp_thirteen/preview_test.html")
        
except Exception as e:
    print(f"错误: {e}")
