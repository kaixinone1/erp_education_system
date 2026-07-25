"""
系统索引管理器
用于快速查询表和字段信息
"""
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class SystemIndexManager:
    """系统索引管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'config', 
                'system_index.json'
            )
        
        self.config_path = config_path
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """加载索引文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "tables": {},
            "fields": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    def _save_index(self):
        """保存索引文件"""
        self.index['updated_at'] = datetime.now().isoformat()
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def add_table(self, table_name: str, chinese_name: str, config_files: List[str] = None):
        """
        添加表到索引
        
        Args:
            table_name: 英文表名
            chinese_name: 中文表名
            config_files: 配置文件列表
        """
        self.index["tables"][table_name] = {
            "chinese_name": chinese_name,
            "config_files": config_files or [],
            "field_count": 0,
            "last_updated": datetime.now().isoformat()
        }
        self._save_index()
    
    def add_field(self, chinese_name: str, english_name: str, table_name: str, data_type: str = "VARCHAR"):
        """
        添加字段到索引
        
        Args:
            chinese_name: 中文字段名
            english_name: 英文字段名
            table_name: 所属表名
            data_type: 数据类型
        """
        if chinese_name not in self.index["fields"]:
            self.index["fields"][chinese_name] = {
                "english_name": english_name,
                "tables": [],
                "data_type": data_type
            }
        
        if table_name not in self.index["fields"][chinese_name]["tables"]:
            self.index["fields"][chinese_name]["tables"].append(table_name)
        
        # 更新表的字段计数
        if table_name in self.index["tables"]:
            self.index["tables"][table_name]["field_count"] += 1
        
        self._save_index()
    
    def get_table(self, table_name: str) -> Optional[Dict]:
        """
        获取表信息
        
        Args:
            table_name: 英文表名
        
        Returns:
            表信息字典
        """
        return self.index["tables"].get(table_name)
    
    def get_field(self, chinese_name: str) -> Optional[Dict]:
        """
        获取字段信息
        
        Args:
            chinese_name: 中文字段名
        
        Returns:
            字段信息字典
        """
        return self.index["fields"].get(chinese_name)
    
    def find_tables_by_field(self, chinese_name: str) -> List[str]:
        """
        根据字段名查找表
        
        Args:
            chinese_name: 中文字段名
        
        Returns:
            表名列表
        """
        field_info = self.get_field(chinese_name)
        if field_info:
            return field_info["tables"]
        return []
    
    def find_fields_by_table(self, table_name: str) -> List[str]:
        """
        根据表名查找字段
        
        Args:
            table_name: 英文表名
        
        Returns:
            中文字段名列表
        """
        fields = []
        for chinese_name, field_info in self.index["fields"].items():
            if table_name in field_info["tables"]:
                fields.append(chinese_name)
        return fields
    
    def rebuild_index(self):
        """
        重建索引（从配置文件重新加载）
        """
        # 清空现有索引
        self.index["tables"] = {}
        self.index["fields"] = {}
        
        # 加载表名映射
        table_name_file = os.path.join(
            os.path.dirname(self.config_path), 
            'table_name_mappings.json'
        )
        if os.path.exists(table_name_file):
            with open(table_name_file, 'r', encoding='utf-8') as f:
                table_mappings = json.load(f)
                
                # 添加表到索引
                for chinese_name, mapping in table_mappings.get("mappings", {}).items():
                    if isinstance(mapping, dict):
                        english_name = mapping.get("english_name")
                        if english_name:
                            self.add_table(english_name, chinese_name)
        
        # 加载字段名映射
        field_name_file = os.path.join(
            os.path.dirname(self.config_path), 
            'field_name_mappings.json'
        )
        if os.path.exists(field_name_file):
            with open(field_name_file, 'r', encoding='utf-8') as f:
                field_mappings = json.load(f)
                
                # 添加字段到索引
                for chinese_name, english_name in field_mappings.get("mappings", {}).items():
                    # 字段可能属于多个表，暂时不关联具体表
                    self.index["fields"][chinese_name] = {
                        "english_name": english_name,
                        "tables": [],
                        "data_type": "VARCHAR"
                    }
        
        self._save_index()
        print("索引重建完成")
