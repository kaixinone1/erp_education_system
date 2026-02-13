#!/usr/bin/env python3
"""
测试字段提取算法
验证提取的点是否在正确的输入框位置
"""
import sys
sys.path.insert(0, 'd:\\erp_thirteen\\tp_education_system\\backend')

from services.field_extractor import extract_pdf_fields
import json

def test_extraction(pdf_path: str):
    """测试字段提取"""
    print(f"\n{'='*60}")
    print(f"测试文件: {pdf_path}")
    print(f"{'='*60}\n")
    
    try:
        fields = extract_pdf_fields(pdf_path)
        
        print(f"共提取到 {len(fields)} 个字段:\n")
        print(f"{'字段名':<20} {'标签':<20} {'页码':<6} {'X坐标':<10} {'Y坐标':<10} {'置信度':<8}")
        print("-" * 80)
        
        for field in fields:
            print(f"{field['name']:<20} {field['label']:<20} {field['page']:<6} "
                  f"{field['x']:<10.1f} {field['y']:<10.1f} {field['confidence']:<8.2f}")
        
        # 保存详细结果
        output_file = pdf_path.replace('.pdf', '_fields.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fields, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细结果已保存到: {output_file}")
        
        return fields
        
    except Exception as e:
        print(f"提取失败: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    # 测试退休呈报表
    pdf_path = "d:\\erp_thirteen\\tp_education_system\\backend\\templates\\职工退休申报表.pdf"
    
    fields = test_extraction(pdf_path)
    
    print("\n" + "="*60)
    print("验证要点:")
    print("1. '姓名'字段的坐标应该在姓名输入框内")
    print("2. '性别'字段的坐标应该在性别选择框内")
    print("3. 所有字段的坐标应该在对应的输入区域")
    print("="*60)
