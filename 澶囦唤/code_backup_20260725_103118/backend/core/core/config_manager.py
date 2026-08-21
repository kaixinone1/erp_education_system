import json
import os
from typing import Any, Dict, Optional

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')

CONFIG_FILES = {
    'navigation': os.path.join(CONFIG_DIR, 'navigation.json'),
    'merged_schema': os.path.join(CONFIG_DIR, 'merged_schema_mappings.json'),
    'ui_components': os.path.join(CONFIG_DIR, 'ui_components.json'),
    'reports': os.path.join(CONFIG_DIR, 'report_definitions.json')
}

def read_config(file_key: str) -> Dict[str, Any]:
    """读取配置文件
    
    Args:
        file_key: 配置文件键名
    
    Returns:
        配置文件内容
    """
    file_path = CONFIG_FILES.get(file_key)
    if not file_path:
        raise ValueError(f"Invalid config file key: {file_key}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_config(file_key: str, data: Dict[str, Any]) -> None:
    """写入配置文件
    
    Args:
        file_key: 配置文件键名
        data: 要写入的数据
    """
    file_path = CONFIG_FILES.get(file_key)
    if not file_path:
        raise ValueError(f"Invalid config file key: {file_key}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_config_files() -> Dict[str, str]:
    """获取所有配置文件路径
    
    Returns:
        配置文件键名到路径的映射
    """
    return CONFIG_FILES.copy()

class ConfigManager:
    """配置管理器类
    
    提供专门的方法来管理各种配置文件
    """
    
    def read_navigation_config(self) -> Dict[str, Any]:
        """读取导航配置
        
        Returns:
            导航配置内容
        """
        return read_config('navigation')
    
    def write_navigation_config(self, data: Dict[str, Any]) -> None:
        """写入导航配置
        
        Args:
            data: 要写入的导航配置数据
        """
        write_config('navigation', data)
    
    def read_merged_schema_config(self) -> Dict[str, Any]:
        """读取合并后的模式映射配置
        
        Returns:
            合并后的模式映射配置内容
        """
        return read_config('merged_schema')
    
    def write_merged_schema_config(self, data: Dict[str, Any]) -> None:
        """写入合并后的模式映射配置
        
        Args:
            data: 要写入的合并后的模式映射配置数据
        """
        write_config('merged_schema', data)
    
    def read_ui_components_config(self) -> Dict[str, Any]:
        """读取UI组件配置
        
        Returns:
            UI组件配置内容
        """
        return read_config('ui_components')
    
    def write_ui_components_config(self, data: Dict[str, Any]) -> None:
        """写入UI组件配置
        
        Args:
            data: 要写入的UI组件配置数据
        """
        write_config('ui_components', data)
    
    def read_reports_config(self) -> Dict[str, Any]:
        """读取报表定义配置
        
        Returns:
            报表定义配置内容
        """
        return read_config('reports')
    
    def write_reports_config(self, data: Dict[str, Any]) -> None:
        """写入报表定义配置
        
        Args:
            data: 要写入的报表定义配置数据
        """
        write_config('reports', data)
    
    def get_config_files(self) -> Dict[str, str]:
        """获取所有配置文件路径
        
        Returns:
            配置文件键名到路径的映射
        """
        return get_config_files()

