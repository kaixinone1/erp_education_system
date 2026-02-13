"""
表名管理器 - 管理中文表名到英文表名的映射，确保唯一性
"""
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime


class TableNameManager:
    """
    表名管理器 - 核心职责：
    1. 维护中文表名到英文表名的唯一映射
    2. 确保同一个中文表名只对应一个英文表名
    3. 导入时进行表名和表结构的重复检查
    """
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        self.config_dir = config_dir
        
        # 中文表名映射文件 - 核心映射关系
        self.table_name_mappings_file = os.path.join(config_dir, 'table_name_mappings.json')
        
        # 加载映射关系
        self.table_name_mappings = self._load_table_name_mappings()
    
    def _load_table_name_mappings(self) -> Dict[str, Dict]:
        """加载中文表名到英文表名的映射关系"""
        try:
            if os.path.exists(self.table_name_mappings_file):
                with open(self.table_name_mappings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载表名映射文件失败: {e}")
        
        return {
            "mappings": {},  # 中文表名 -> {english_name, table_type, created_at}
            "reverse_mappings": {}  # 英文表名 -> 中文表名
        }
    
    def _save_table_name_mappings(self):
        """保存表名映射关系"""
        try:
            with open(self.table_name_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(self.table_name_mappings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存表名映射文件失败: {e}")
    
    def check_table_name(
        self, 
        chinese_name: str, 
        field_configs: List[Dict],
        table_type: str = "master"
    ) -> Tuple[str, str, Optional[str]]:
        """
        检查表名，返回处理结果
        
        :param chinese_name: 中文表名
        :param field_configs: 字段配置列表
        :param table_type: 表类型
        :return: (status, message, english_name)
            status: 
                - 'existing' - 中文表名已存在，表结构一致，直接使用
                - 'structure_mismatch' - 中文表名已存在，但表结构不一致，需要修改中文表名
                - 'name_conflict' - 中文表名不重复，但表结构相同，需要用户确认
                - 'new_table' - 新表，可以创建
        """
        # 1. 首先检查中文表名是否已存在
        if chinese_name in self.table_name_mappings.get("mappings", {}):
            existing_mapping = self.table_name_mappings["mappings"][chinese_name]
            existing_english_name = existing_mapping.get("english_name")
            
            # 获取现有表的字段签名
            from sqlalchemy import create_engine, text
            DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
            engine = create_engine(DATABASE_URL)
            
            existing_signature = self._get_table_signature_from_db(engine, existing_english_name)
            new_signature = self._get_signature_from_configs(field_configs)
            
            if existing_signature and self._compare_signatures(existing_signature, new_signature):
                # 表结构完全一致，直接使用现有表
                return 'existing', f'中文表名"{chinese_name}"已存在，表结构一致，将使用现有表"{existing_english_name}"', existing_english_name
            else:
                # 表结构不一致，需要修改中文表名
                return 'structure_mismatch', f'中文表名"{chinese_name}"已存在，但表结构不一致。请修改中文表名后重新导入。', None
        
        # 2. 中文表名不存在，检查是否有表结构相同的表
        from sqlalchemy import create_engine, text
        DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
        engine = create_engine(DATABASE_URL)
        
        new_signature = self._get_signature_from_configs(field_configs)
        
        # 查询数据库中所有表
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            db_tables = [row[0] for row in result]
        
        # 检查是否有表结构相同的表
        for table_name in db_tables:
            existing_signature = self._get_table_signature_from_db(engine, table_name)
            if existing_signature and self._compare_signatures(existing_signature, new_signature):
                # 找到表结构相同的表，需要用户确认
                return 'name_conflict', f'发现表结构相同的表"{table_name}"。请确认是否使用该表，或修改中文表名创建新表。', table_name
        
        # 3. 新表，可以创建
        return 'new_table', '新表，可以创建', None
    
    def register_table_name(
        self, 
        chinese_name: str, 
        english_name: str, 
        table_type: str = "master",
        field_configs: List[Dict] = None
    ) -> bool:
        """
        注册新的表名映射关系
        
        :param chinese_name: 中文表名
        :param english_name: 英文表名
        :param table_type: 表类型
        :param field_configs: 字段配置（用于保存表结构签名）
        :return: 是否成功
        """
        # 检查中文表名是否已存在
        if chinese_name in self.table_name_mappings.get("mappings", {}):
            print(f"中文表名'{chinese_name}'已存在，不能重复注册")
            return False
        
        # 检查英文表名是否已被其他中文表名使用
        if english_name in self.table_name_mappings.get("reverse_mappings", {}):
            existing_chinese = self.table_name_mappings["reverse_mappings"][english_name]
            if existing_chinese != chinese_name:
                print(f"英文表名'{english_name}'已被中文表名'{existing_chinese}'使用")
                return False
        
        # 保存字段签名
        field_signature = None
        if field_configs:
            field_signature = self._get_signature_from_configs(field_configs)
        
        # 注册映射关系
        self.table_name_mappings["mappings"][chinese_name] = {
            "english_name": english_name,
            "table_type": table_type,
            "created_at": datetime.now().isoformat(),
            "field_signature": field_signature
        }
        
        self.table_name_mappings["reverse_mappings"][english_name] = chinese_name
        
        # 保存到文件
        self._save_table_name_mappings()
        
        print(f"注册表名映射: '{chinese_name}' -> '{english_name}'")
        return True
    
    def get_english_name(self, chinese_name: str) -> Optional[str]:
        """根据中文表名获取英文表名"""
        mapping = self.table_name_mappings.get("mappings", {}).get(chinese_name)
        return mapping.get("english_name") if mapping else None
    
    def get_chinese_name(self, english_name: str) -> Optional[str]:
        """根据英文表名获取中文表名"""
        return self.table_name_mappings.get("reverse_mappings", {}).get(english_name)
    
    def _get_signature_from_configs(self, field_configs: List[Dict]) -> List[tuple]:
        """从字段配置获取表签名"""
        signature = []
        for field in field_configs:
            target_field = field.get('targetField', '')
            data_type = field.get('dataType', 'VARCHAR')
            if target_field:
                normalized_type = self._normalize_data_type(data_type)
                signature.append((target_field.lower(), normalized_type))
        return sorted(signature)
    
    def _get_table_signature_from_db(self, engine, table_name: str) -> Optional[List[tuple]]:
        """从数据库获取表的字段签名"""
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name AND table_schema = 'public'
                    ORDER BY column_name
                """), {"table_name": table_name})
                
                signature = []
                for row in result:
                    col_name = row[0]
                    data_type = row[1]
                    # 跳过系统字段和外键字段
                    if col_name in ['id', 'created_at', 'updated_at', 'import_batch', 'code', 'teacher_id']:
                        continue
                    normalized_type = self._normalize_data_type(data_type)
                    signature.append((col_name.lower(), normalized_type))
                
                return sorted(signature)
        except Exception as e:
            print(f"获取表 {table_name} 签名失败: {e}")
            return None
    
    def _compare_signatures(self, sig1: List[tuple], sig2: List[tuple]) -> bool:
        """比较两个表签名是否完全一致"""
        if len(sig1) != len(sig2):
            return False
        
        for i in range(len(sig1)):
            if sig1[i] != sig2[i]:
                return False
        
        return True
    
    def _normalize_data_type(self, data_type: str) -> str:
        """标准化数据类型名称"""
        type_mapping = {
            'VARCHAR': 'STRING',
            'CHARACTER VARYING': 'STRING',
            'CHAR': 'STRING',
            'TEXT': 'STRING',
            'INTEGER': 'INTEGER',
            'INT': 'INTEGER',
            'BIGINT': 'INTEGER',
            'DECIMAL': 'DECIMAL',
            'NUMERIC': 'DECIMAL',
            'FLOAT': 'DECIMAL',
            'DOUBLE': 'DECIMAL',
            'DATE': 'DATE',
            'DATETIME': 'DATETIME',
            'TIMESTAMP': 'DATETIME',
            'BOOLEAN': 'BOOLEAN',
            'BOOL': 'BOOLEAN'
        }

        upper_type = str(data_type).upper()
        return type_mapping.get(upper_type, upper_type)
    
    def get_all_mappings(self) -> Dict[str, Dict]:
        """获取所有表名映射"""
        return self.table_name_mappings.get("mappings", {})
