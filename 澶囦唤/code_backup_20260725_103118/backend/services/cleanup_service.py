"""
数据清理服务 - 支持删除表数据和结构，清理相关配置
"""

import json
import os
from typing import List, Dict, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor


class CleanupService:
    """数据清理服务"""
    
    # 系统核心表，不能删除
    # 注意：这里只保留真正的系统表，业务表不应该加在这里
    SYSTEM_TABLES = []
    
    def __init__(self, db_params: Dict = None, config_dir: str = None):
        # 数据库连接参数
        if db_params is None:
            self.db_params = {
                'host': 'localhost',
                'database': 'taiping_education',
                'user': 'taiping_user',
                'password': 'taiping_password'
            }
        else:
            self.db_params = db_params
        
        # 配置文件目录
        if config_dir is None:
            self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        else:
            self.config_dir = config_dir
        
        # 表名映射文件
        self.table_name_mappings_file = os.path.join(self.config_dir, 'table_name_mappings.json')
        # 字段配置目录
        self.field_configs_dir = os.path.join(self.config_dir, 'field_configs')
        # 导航配置文件
        self.navigation_file = os.path.join(self.config_dir, 'navigation.json')
    
    def get_deletable_tables(self) -> List[Dict]:
        """
        获取可删除的表列表（显示中文表名）
        从数据库获取所有表，然后匹配中文名
        
        Returns:
            表列表，包含中文名、英文名、表类型
        """
        tables = []
        
        # 读取表名映射
        mappings = self._load_table_name_mappings()
        reverse_mappings = mappings.get('reverse_mappings', {})
        
        # 从数据库获取所有表
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            db_tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"获取数据库表列表失败: {e}")
            db_tables = []
        
        # 处理每个表
        for english_name in db_tables:
            # 排除系统表
            if english_name in self.SYSTEM_TABLES:
                continue
            
            # 尝试从映射中获取中文名和类型
            chinese_name = english_name  # 默认使用英文名
            table_type = 'master'
            
            if english_name in reverse_mappings:
                mapping_info = reverse_mappings[english_name]
                if isinstance(mapping_info, dict):
                    chinese_name = mapping_info.get('chinese_name', english_name)
                    table_type = mapping_info.get('table_type', 'master')
                elif isinstance(mapping_info, str):
                    chinese_name = mapping_info
            
            tables.append({
                'chinese_name': chinese_name,
                'english_name': english_name,
                'table_type': table_type,
                'exists_in_db': True
            })
        
        return tables
    
    def cleanup_table(self, chinese_name: str) -> Dict:
        """
        清理表数据和结构
        
        Args:
            chinese_name: 中文表名（或英文名，如果没有中文映射）
            
        Returns:
            清理结果
        """
        result = {
            'success': False,
            'messages': [],
            'errors': []
        }
        
        try:
            # 1. 获取英文表名
            mappings = self._load_table_name_mappings()
            table_info = mappings.get('mappings', {}).get(chinese_name)
            
            if table_info:
                # 有中文映射
                english_name = table_info.get('english_name')
            else:
                # 没有中文映射，可能是直接使用英文名
                english_name = chinese_name
                chinese_name = None  # 没有中文名
            
            # 检查是否是系统表
            if english_name in self.SYSTEM_TABLES:
                result['errors'].append(f'不能删除系统表 "{english_name}"')
                return result
            
            # 确定显示名称（优先使用中文名）
            display_name = chinese_name or english_name
            
            # 2. 删除数据库表
            if self._check_table_exists(english_name):
                self._drop_table(english_name)
                result['messages'].append(f'已删除数据库表: {display_name}')
            else:
                result['messages'].append(f'数据库表不存在: {display_name}')
            
            # 3. 清理表名映射（无论是否有中文名，都尝试清理）
            mapping_removed = self._remove_table_name_mapping_by_english(english_name)
            if mapping_removed:
                result['messages'].append(f'已清理表名映射: {display_name}')
            
            # 4. 清理字段配置（尝试中文名和英文名）
            config_removed = False
            if chinese_name:
                config_removed = self._remove_field_config(chinese_name) or config_removed
            config_removed = self._remove_field_config(english_name) or config_removed
            if config_removed:
                result['messages'].append(f'已清理字段配置: {display_name}')
            
            # 5. 清理其他表对该表的关联引用（如果是字典表）
            if table_info and table_info.get('table_type') == 'dictionary':
                refs_removed = self._remove_dictionary_references(english_name, chinese_name or english_name)
                if refs_removed > 0:
                    result['messages'].append(f'已清理 {refs_removed} 个子表对 {display_name} 的关联引用')
            
            # 注意：不清理导航配置（navigation.json），菜单结构应该保留
            
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(str(e))
        
        return result
    
    def _load_table_name_mappings(self) -> Dict:
        """加载表名映射"""
        try:
            if os.path.exists(self.table_name_mappings_file):
                with open(self.table_name_mappings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载表名映射失败: {e}")
        
        return {'mappings': {}, 'reverse_mappings': {}}
    
    def _save_table_name_mappings(self, mappings: Dict):
        """保存表名映射"""
        try:
            with open(self.table_name_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(mappings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存表名映射失败: {e}")
    
    def _check_table_exists(self, table_name: str) -> bool:
        """检查表是否存在于数据库"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = %s
                )
            """, (table_name,))
            exists = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return exists
        except Exception as e:
            print(f"检查表存在性失败: {e}")
            return False
    
    def _drop_table(self, table_name: str):
        """删除数据库表"""
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        conn.commit()
        cursor.close()
        conn.close()
    
    def _remove_table_name_mapping(self, chinese_name: str):
        """从表名映射中移除（通过中文名）"""
        mappings = self._load_table_name_mappings()
        
        if chinese_name in mappings.get('mappings', {}):
            english_name = mappings['mappings'][chinese_name].get('english_name')
            
            # 删除正向映射
            del mappings['mappings'][chinese_name]
            
            # 删除反向映射
            if english_name and english_name in mappings.get('reverse_mappings', {}):
                del mappings['reverse_mappings'][english_name]
            
            self._save_table_name_mappings(mappings)
    
    def _remove_table_name_mapping_by_english(self, english_name: str) -> bool:
        """从表名映射中移除（通过英文名）"""
        mappings = self._load_table_name_mappings()
        removed = False
        
        # 从反向映射中找到中文名
        chinese_name = None
        if english_name in mappings.get('reverse_mappings', {}):
            reverse_value = mappings['reverse_mappings'][english_name]
            if isinstance(reverse_value, str):
                chinese_name = reverse_value
            elif isinstance(reverse_value, dict):
                chinese_name = reverse_value.get('chinese_name')
            
            # 删除反向映射
            del mappings['reverse_mappings'][english_name]
            removed = True
        
        # 从正向映射中删除
        if chinese_name and chinese_name in mappings.get('mappings', {}):
            del mappings['mappings'][chinese_name]
            removed = True
        
        # 如果没有找到中文名，遍历正向映射查找
        if not chinese_name:
            for cn_name, info in list(mappings.get('mappings', {}).items()):
                if info.get('english_name') == english_name:
                    del mappings['mappings'][cn_name]
                    removed = True
                    break
        
        if removed:
            self._save_table_name_mappings(mappings)
        
        return removed
    
    def _remove_field_config(self, chinese_name: str) -> bool:
        """删除字段配置文件"""
        try:
            # 尝试多种可能的文件名
            possible_names = [
                chinese_name,
                chinese_name.replace(' ', '_'),
                chinese_name.replace(' ', '-')
            ]
            
            removed = False
            for name in possible_names:
                config_file = os.path.join(self.field_configs_dir, f"{name}.json")
                if os.path.exists(config_file):
                    os.remove(config_file)
                    removed = True
            
            return removed
        except Exception as e:
            print(f"删除字段配置失败: {e}")
            return False
    
    def _remove_from_navigation(self, chinese_name: str, english_name: str) -> bool:
        """从导航配置中移除"""
        try:
            if not os.path.exists(self.navigation_file):
                return False
            
            with open(self.navigation_file, 'r', encoding='utf-8') as f:
                nav_config = json.load(f)
            
            removed = False
            
            # 遍历所有模块，查找并删除
            for module in nav_config.get('modules', []):
                # 检查子模块
                if 'children' in module:
                    module['children'] = [
                        child for child in module['children']
                        if child.get('title') != chinese_name and child.get('name') != english_name
                    ]
                    if len(module['children']) < len([c for c in module.get('children', []) if c.get('title') == chinese_name or c.get('name') == english_name]):
                        removed = True
                
                # 检查数据节点
                if 'dataNodes' in module:
                    module['dataNodes'] = [
                        node for node in module['dataNodes']
                        if node.get('title') != chinese_name and node.get('name') != english_name
                    ]
                    if len(module['dataNodes']) < len([n for n in module.get('dataNodes', []) if n.get('title') == chinese_name or n.get('name') == english_name]):
                        removed = True
            
            if removed:
                with open(self.navigation_file, 'w', encoding='utf-8') as f:
                    json.dump(nav_config, f, ensure_ascii=False, indent=2)
            
            return removed
        except Exception as e:
            print(f"清理导航配置失败: {e}")
            return False
    
    def _remove_dictionary_references(self, dict_table_name: str, dict_chinese_name: str) -> int:
        """
        清理其他子表对字典表的关联引用
        
        Args:
            dict_table_name: 字典表英文名
            dict_chinese_name: 字典表中文名
            
        Returns:
            清理的引用数量
        """
        removed_count = 0
        
        try:
            # 遍历所有字段配置文件，查找对该字典表的引用
            if not os.path.exists(self.field_configs_dir):
                return removed_count
            
            for filename in os.listdir(self.field_configs_dir):
                if not filename.endswith('.json'):
                    continue
                
                config_file = os.path.join(self.field_configs_dir, filename)
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    fields = config.get('fields', [])
                    modified = False
                    
                    # 查找并修改对该字典表的引用
                    for field in fields:
                        if field.get('dictionary_table') == dict_table_name:
                            # 清除字典关联
                            field['dictionary_table'] = None
                            field['link_to_dictionary'] = False
                            field['value_mapping'] = {}
                            modified = True
                            removed_count += 1
                    
                    # 保存修改后的配置
                    if modified:
                        with open(config_file, 'w', encoding='utf-8') as f:
                            json.dump(config, f, ensure_ascii=False, indent=2)
                        
                except Exception as e:
                    print(f"处理字段配置文件 {filename} 失败: {e}")
            
            return removed_count
        except Exception as e:
            print(f"清理字典表引用失败: {e}")
            return removed_count
