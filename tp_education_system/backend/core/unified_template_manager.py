"""
统一模板管理器
实现：导入模板 = 网页呈现模板 = 导出模板
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from docx import Document


class UnifiedTemplateManager:
    """统一模板管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'config', 
                'unified_template_config.json'
            )
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "templates": {},
            "template_categories": {},
            "template_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def _save_config(self):
        """保存配置文件"""
        self.config['updated_at'] = datetime.now().isoformat()
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def parse_excel_template(self, file_path: str, template_name: str = None) -> Dict:
        """
        解析Excel模板文件
        
        Args:
            file_path: Excel文件路径
            template_name: 模板名称（可选）
        
        Returns:
            模板配置字典
        """
        if template_name is None:
            template_name = os.path.splitext(os.path.basename(file_path))[0]
        
        df = pd.read_excel(file_path, nrows=0)
        fields = []
        english_names_used = set()
        
        for idx, col_name in enumerate(df.columns):
            chinese_name = str(col_name)
            english_name = self._generate_unique_english_name(
                chinese_name, 
                english_names_used
            )
            english_names_used.add(english_name)
            
            field_config = {
                "chinese_name": chinese_name,
                "english_name": english_name,
                "column_index": idx,
                "data_type": "VARCHAR",
                "length": 255,
                "required": False,
                "display_order": idx
            }
            fields.append(field_config)
        
        template_config = {
            "template_id": self._generate_template_id(template_name),
            "chinese_name": template_name,
            "english_name": self._generate_english_name(template_name),
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "source_file": os.path.basename(file_path),
            
            "import_config": {
                "file_type": "xlsx",
                "sheet_name": "Sheet1",
                "start_row": 2,
                "fields": fields
            },
            
            "display_config": {
                "form_layout": "horizontal",
                "columns_per_row": 3,
                "fields": [
                    {
                        "chinese_name": field["chinese_name"],
                        "english_name": field["english_name"],
                        "display_name": field["chinese_name"],
                        "input_type": "text",
                        "placeholder": f"请输入{field['chinese_name']}",
                        "required": field["required"]
                    }
                    for field in fields
                ]
            },
            
            "export_config": {
                "file_type": "xlsx",
                "template_file": file_path,
                "sheet_name": "Sheet1",
                "start_row": 2,
                "fields": [
                    {
                        "chinese_name": field["chinese_name"],
                        "english_name": field["english_name"],
                        "column_index": field["column_index"]
                    }
                    for field in fields
                ]
            }
        }
        
        return template_config
    
    def parse_word_template(self, file_path: str, template_name: str = None) -> Dict:
        """
        解析Word模板文件
        
        Args:
            file_path: Word文件路径
            template_name: 模板名称（可选）
        
        Returns:
            模板配置字典
        """
        if template_name is None:
            template_name = os.path.splitext(os.path.basename(file_path))[0]
        
        doc = Document(file_path)
        placeholders = set()
        
        for paragraph in doc.paragraphs:
            import re
            matches = re.findall(r'\{([^{}]+)\}', paragraph.text)
            placeholders.update(matches)
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    import re
                    matches = re.findall(r'\{([^{}]+)\}', cell.text)
                    placeholders.update(matches)
        
        fields = []
        for idx, placeholder in enumerate(sorted(placeholders)):
            field_config = {
                "chinese_name": placeholder,
                "english_name": self._generate_english_name(placeholder),
                "placeholder": f"{{{placeholder}}}",
                "data_type": "VARCHAR",
                "length": 255,
                "required": False,
                "display_order": idx
            }
            fields.append(field_config)
        
        template_config = {
            "template_id": self._generate_template_id(template_name),
            "chinese_name": template_name,
            "english_name": self._generate_english_name(template_name),
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "source_file": os.path.basename(file_path),
            
            "import_config": {
                "file_type": "docx",
                "fields": fields
            },
            
            "display_config": {
                "form_layout": "vertical",
                "fields": [
                    {
                        "chinese_name": field["chinese_name"],
                        "english_name": field["english_name"],
                        "display_name": field["chinese_name"],
                        "input_type": "text",
                        "placeholder": f"请输入{field['chinese_name']}",
                        "required": field["required"]
                    }
                    for field in fields
                ]
            },
            
            "export_config": {
                "file_type": "docx",
                "template_file": file_path,
                "fields": [
                    {
                        "chinese_name": field["chinese_name"],
                        "english_name": field["english_name"],
                        "placeholder": field["placeholder"]
                    }
                    for field in fields
                ]
            }
        }
        
        return template_config
    
    def save_template(self, template_config: Dict) -> bool:
        """
        保存模板配置
        
        Args:
            template_config: 模板配置字典
        
        Returns:
            是否保存成功
        """
        template_id = template_config["template_id"]
        self.config["templates"][template_id] = template_config
        self._save_config()
        return True
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """
        获取模板配置
        
        Args:
            template_id: 模板ID
        
        Returns:
            模板配置字典
        """
        return self.config["templates"].get(template_id)
    
    def list_templates(self, category: str = None) -> List[Dict]:
        """
        列出所有模板
        
        Args:
            category: 模板分类（可选）
        
        Returns:
            模板列表
        """
        templates = list(self.config["templates"].values())
        
        if category:
            templates = [
                t for t in templates 
                if t.get("category") == category
            ]
        
        return templates
    
    def delete_template(self, template_id: str) -> bool:
        """
        删除模板
        
        Args:
            template_id: 模板ID
        
        Returns:
            是否删除成功
        """
        if template_id in self.config["templates"]:
            del self.config["templates"][template_id]
            self._save_config()
            return True
        return False
    
    def _generate_template_id(self, template_name: str) -> str:
        """生成模板ID"""
        import hashlib
        timestamp = datetime.now().isoformat()
        unique_str = f"{template_name}_{timestamp}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]
    
    def _generate_english_name(self, chinese_name: str) -> str:
        """
        生成英文名称（使用FieldNameManager）
        
        Args:
            chinese_name: 中文名称
        
        Returns:
            英文名称
        """
        from .field_name_manager import FieldNameManager
        
        field_name_manager = FieldNameManager()
        english_name = field_name_manager.get_or_create_mapping(chinese_name)
        
        return english_name
    
    def _generate_unique_english_name(self, chinese_name: str, used_names: set) -> str:
        """
        生成唯一的英文名称
        
        Args:
            chinese_name: 中文名称
            used_names: 已使用的英文名称集合
        
        Returns:
            唯一的英文名称
        """
        base_english_name = self._generate_english_name(chinese_name)
        
        if base_english_name not in used_names:
            return base_english_name
        
        counter = 1
        while f"{base_english_name}_{counter}" in used_names:
            counter += 1
        
        return f"{base_english_name}_{counter}"
