#!/usr/bin/env python3
"""
翻译服务 - 集成翻译API并缓存结果
优先使用百度翻译（国内可用），后备使用Google翻译
"""
import json
import os
import re
import hashlib
import requests
from typing import Optional

# 翻译缓存文件
TRANSLATION_CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'translation_cache.json')

# 百度翻译API配置（需要用户申请）
BAIDU_APP_ID = os.environ.get('BAIDU_APP_ID', '')
BAIDU_SECRET_KEY = os.environ.get('BAIDU_SECRET_KEY', '')


class TranslationService:
    """翻译服务 - 使用百度翻译API（国内可用）"""
    
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
        self.cache = self._load_cache()
        self.use_baidu = bool(BAIDU_APP_ID and BAIDU_SECRET_KEY)
        self.use_google = False  # 默认不使用Google（国内访问困难）
        print(f"翻译服务初始化: 百度API={'已配置' if self.use_baidu else '未配置'}")
    
    def _load_cache(self) -> dict:
        """加载翻译缓存"""
        if os.path.exists(TRANSLATION_CACHE_FILE):
            try:
                with open(TRANSLATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载翻译缓存失败: {e}")
        return {}
    
    def _save_cache(self):
        """保存翻译缓存"""
        try:
            os.makedirs(os.path.dirname(TRANSLATION_CACHE_FILE), exist_ok=True)
            with open(TRANSLATION_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存翻译缓存失败: {e}")
    
    def _translate_with_baidu(self, chinese_text: str) -> Optional[str]:
        """使用百度翻译API"""
        if not self.use_baidu:
            return None
        
        try:
            import random
            salt = random.randint(32768, 65536)
            sign = hashlib.md5(f"{BAIDU_APP_ID}{chinese_text}{salt}{BAIDU_SECRET_KEY}".encode()).hexdigest()
            
            url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
            params = {
                'q': chinese_text,
                'from': 'zh',
                'to': 'en',
                'appid': BAIDU_APP_ID,
                'salt': salt,
                'sign': sign
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
            else:
                print(f"百度翻译错误: {result.get('error_msg', '未知错误')}")
        except Exception as e:
            print(f"百度翻译失败: {e}")
        
        return None
    
    def _translate_with_google(self, chinese_text: str) -> Optional[str]:
        """使用Google翻译（需要翻墙）"""
        if not self.use_google:
            return None
        
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='zh-CN', target='en')
            return translator.translate(chinese_text)
        except Exception as e:
            print(f"Google翻译失败: {e}")
        
        return None
    
    def _normalize_field_name(self, translation: str) -> str:
        """
        将翻译结果规范化为数据库字段名
        例如："Date of Birth" -> "date_of_birth"
        """
        # 转换为小写
        result = translation.lower()
        # 替换特殊字符为空格
        result = re.sub(r'[^a-z0-9\u4e00-\u9fff]', ' ', result)
        # 替换多个空格为单个空格
        result = re.sub(r'\s+', ' ', result).strip()
        # 替换空格为下划线
        result = result.replace(' ', '_')
        # 移除连续的下划线
        result = re.sub(r'_+', '_', result)
        return result
    
    def translate(self, chinese_text: str) -> Optional[str]:
        """
        翻译中文为英文字段名
        优先使用缓存，如果没有则调用翻译API
        """
        chinese_text = chinese_text.strip()
        
        # 1. 检查缓存
        if chinese_text in self.cache:
            print(f"使用缓存翻译: {chinese_text} -> {self.cache[chinese_text]}")
            return self.cache[chinese_text]
        
        # 2. 尝试百度翻译
        if self.use_baidu:
            print(f"使用百度翻译: {chinese_text}...")
            translation = self._translate_with_baidu(chinese_text)
            if translation:
                field_name = self._normalize_field_name(translation)
                self.cache[chinese_text] = field_name
                self._save_cache()
                print(f"百度翻译成功: {chinese_text} -> {field_name}")
                return field_name
        
        # 3. 尝试Google翻译（如果启用）
        if self.use_google:
            print(f"使用Google翻译: {chinese_text}...")
            translation = self._translate_with_google(chinese_text)
            if translation:
                field_name = self._normalize_field_name(translation)
                self.cache[chinese_text] = field_name
                self._save_cache()
                print(f"Google翻译成功: {chinese_text} -> {field_name}")
                return field_name
        
        return None
    
    def is_available(self) -> bool:
        """检查翻译服务是否可用"""
        return self.use_baidu or self.use_google


# 全局翻译服务实例
translation_service = TranslationService()
