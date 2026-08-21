#!/usr/bin/env python3
"""
拼音转换服务 - 将中文转换为拼音
"""
import re
from typing import List

try:
    from pypinyin import pinyin, Style
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False
    print("警告：pypinyin库未安装，拼音转换功能不可用")
    print("安装方法：pip install pypinyin")


class PinyinService:
    """拼音转换服务"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.available = PYPINYIN_AVAILABLE
    
    def convert_to_pinyin(self, chinese_text: str) -> str:
        """
        将中文转换为拼音
        例如："岗位聘任信息" -> "gang_wei_pin_ren_xin_xi"
        """
        if not self.available:
            return None
        
        try:
            # 转换为拼音列表
            pinyin_list = pinyin(chinese_text, style=Style.NORMAL)
            # 提取拼音
            pinyin_words = [item[0] for item in pinyin_list]
            # 组合为下划线分隔的字符串
            result = '_'.join(pinyin_words)
            return result
        except Exception as e:
            print(f"拼音转换失败: {e}")
            return None
    
    def is_available(self) -> bool:
        """检查拼音服务是否可用"""
        return self.available


# 全局拼音服务实例
pinyin_service = PinyinService()
