#!/usr/bin/env python3
"""
测试表名翻译逻辑
"""
import sys
sys.path.insert(0, 'd:\\erp_thirteen\\tp_education_system\\backend')

from core.metadata_engine import MetadataEngine, CORE_ENTITY_DICT, BUSINESS_OBJECT_DICT

def test_smart_translate():
    """测试智能分词翻译"""
    engine = MetadataEngine()
    
    test_cases = [
        ("学历类型字典", "dictionary"),
        ("教师基础信息", "master"),
        ("部门信息", "master"),
        ("学历层次字典", "dictionary"),
        ("职务字典", "dictionary"),
        ("员工考勤记录", "master"),
        ("培训课程信息", "master"),
    ]
    
    print("=" * 60)
    print("表名翻译测试")
    print("=" * 60)
    
    for chinese_name, table_type in test_cases:
        result = engine.translate_table_name(chinese_name, table_type=table_type)
        print(f"\n中文: {chinese_name}")
        print(f"类型: {table_type}")
        print(f"英文: {result}")
        
        # 测试分词结果
        parts = engine._smart_translate_table_name(chinese_name)
        print(f"分词: {parts}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_smart_translate()
