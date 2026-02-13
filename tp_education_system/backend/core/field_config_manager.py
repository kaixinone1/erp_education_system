"""
字段配置管理器 - 参考 erp_twelve 实现
统一管理字段配置的保存、加载和版本控制
"""

import json
import os
import uuid
import shutil
from typing import Dict, Any, List, Optional
from datetime import datetime


class FieldConfigManager:
    """字段配置管理器"""

    def __init__(self, config_dir: str = None):
        """
        初始化字段配置管理器

        Args:
            config_dir: 配置文件目录，默认使用 backend/config
        """
        if config_dir is None:
            current_dir = os.path.dirname(os.path.dirname(__file__))
            self.config_dir = os.path.join(current_dir, 'config')
        else:
            self.config_dir = config_dir

        # 统一配置文件路径
        self.field_mappings_file = os.path.join(self.config_dir, 'field_mappings.json')

        # 单个配置文件目录（向后兼容）
        self.field_configs_dir = os.path.join(self.config_dir, 'field_configs')
        os.makedirs(self.field_configs_dir, exist_ok=True)

        # 缓存
        self._cache: Optional[Dict[str, Any]] = None

    def _load_field_mappings(self) -> Dict[str, Any]:
        """加载 field_mappings.json"""
        if self._cache is not None:
            return self._cache

        try:
            if os.path.exists(self.field_mappings_file):
                with open(self.field_mappings_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                    return self._cache
        except Exception as e:
            print(f"加载 field_mappings.json 失败: {e}")

        # 文件不存在或加载失败，返回默认结构
        return {"configs": [], "global_mappings": {}}

    def _save_field_mappings(self, data: Dict[str, Any]) -> bool:
        """保存 field_mappings.json（带备份回滚机制）"""
        backup_file = f"{self.field_mappings_file}.bak"

        # 备份现有文件
        if os.path.exists(self.field_mappings_file):
            shutil.copy2(self.field_mappings_file, backup_file)

        try:
            with open(self.field_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 更新缓存
            self._cache = data

            # 删除备份
            if os.path.exists(backup_file):
                os.remove(backup_file)

            return True
        except Exception as e:
            print(f"保存 field_mappings.json 失败: {e}")
            # 恢复备份
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, self.field_mappings_file)
                os.remove(backup_file)
            return False

    def get_all_configs(self) -> List[Dict[str, Any]]:
        """获取所有字段配置"""
        data = self._load_field_mappings()
        return data.get('configs', [])

    def get_config_by_id(self, config_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取配置"""
        configs = self.get_all_configs()
        for config in configs:
            if config.get('id') == config_id:
                return config
        return None

    def get_config_by_table_name(self, table_name: str) -> Optional[Dict[str, Any]]:
        """根据表名获取配置"""
        configs = self.get_all_configs()
        for config in configs:
            if config.get('table_name') == table_name and config.get('is_latest', False):
                return config
        return None

    def get_config_by_name(self, config_name: str) -> Optional[Dict[str, Any]]:
        """根据配置名称获取配置"""
        configs = self.get_all_configs()
        for config in configs:
            if config.get('config_name') == config_name and config.get('is_latest', False):
                return config
        return None

    def save_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存字段配置（核心方法）

        Args:
            config_data: 配置数据，包含：
                - config_name: 配置名称（中文表名）
                - table_name: 英文表名
                - field_mappings: 字段映射列表
                - table_type: 表类型（master/detail/dictionary）
                - parent_table: 父表名（子表用）
                - source_file_pattern: 源文件匹配模式

        Returns:
            保存结果字典
        """
        config_name = config_data.get('config_name', '')
        table_name = config_data.get('table_name', '')

        if not config_name:
            return {'success': False, 'message': '配置名称不能为空'}

        # 加载现有配置
        data = self._load_field_mappings()
        configs = data.get('configs', [])
        global_mappings = data.get('global_mappings', {})

        # 检查配置名称是否重复（排除当前编辑的配置）
        existing_config = self.get_config_by_name(config_name)
        if existing_config and existing_config.get('id') != config_data.get('id'):
            return {
                'success': False,
                'message': f'配置名称 "{config_name}" 已存在',
                'status': 'name_conflict'
            }

        # 检查英文表名是否重复
        if table_name:
            existing_by_table = self.get_config_by_table_name(table_name)
            if existing_by_table and existing_by_table.get('id') != config_data.get('id'):
                return {
                    'success': False,
                    'message': f'英文表名 "{table_name}" 已被 "{existing_by_table.get("config_name")}" 使用',
                    'status': 'table_name_conflict'
                }

        # 更新全局字段映射
        field_mappings = config_data.get('field_mappings', [])
        for mapping in field_mappings:
            chinese_field = mapping.get('sourceField') or mapping.get('chinese_name')
            english_field = mapping.get('targetField') or mapping.get('english_name')

            if chinese_field and english_field:
                # 检查是否有冲突
                if chinese_field in global_mappings:
                    existing = global_mappings[chinese_field]
                    if existing != english_field:
                        print(f"警告: 字段映射冲突 '{chinese_field}' -> '{existing}' vs '{english_field}'")
                else:
                    global_mappings[chinese_field] = english_field

        # 准备配置数据
        now = datetime.now().isoformat()

        # 生成或保留ID
        config_id = config_data.get('id')
        if not config_id:
            config_id = f"config_{str(uuid.uuid4())[:8]}"

        # 查找是否已存在相同配置
        existing_index = None
        for i, config in enumerate(configs):
            if config.get('id') == config_id:
                existing_index = i
                break

        # 构建新的配置数据
        new_config = {
            'id': config_id,
            'config_name': config_name,
            'table_name': table_name,
            'table_type': config_data.get('table_type', 'master'),
            'parent_table': config_data.get('parent_table', ''),
            'source_file_pattern': config_data.get('source_file_pattern', f"*{config_name}*"),
            'field_mappings': field_mappings,
            'version': 1,
            'is_latest': True,
            'created_at': now,
            'updated_at': now
        }

        # 如果已存在，保留创建时间并增加版本号
        if existing_index is not None:
            old_config = configs[existing_index]
            new_config['created_at'] = old_config.get('created_at', now)
            new_config['version'] = old_config.get('version', 1) + 1
            configs[existing_index] = new_config
        else:
            configs.append(new_config)

        # 保存到 field_mappings.json
        data['configs'] = configs
        data['global_mappings'] = global_mappings

        if not self._save_field_mappings(data):
            return {'success': False, 'message': '保存配置文件失败'}

        # 同时保存到单个配置文件（向后兼容）
        self._save_single_config_file(new_config)

        # 更新 merged_schema_mappings.json
        self._update_merged_schema_config(new_config)

        return {
            'success': True,
            'message': f'配置 "{config_name}" 保存成功',
            'config_id': config_id,
            'is_new': existing_index is None
        }

    def _update_merged_schema_config(self, config: Dict[str, Any]):
        """
        更新 merged_schema_mappings.json
        保存表结构和字段关联关系
        """
        try:
            from datetime import datetime

            config_name = config.get('config_name', '')
            table_name = config.get('table_name', '')
            table_type = config.get('table_type', 'master')
            parent_table = config.get('parent_table', '')
            field_mappings = config.get('field_mappings', [])

            if not table_name:
                return

            # 加载 merged_schema_mappings.json
            schema_file = os.path.join(self.config_dir, 'merged_schema_mappings.json')
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_config = json.load(f)
            except:
                schema_config = {"tables": {}, "mappings": {}, "validation_rules": {}}

            # 更新 tables
            if "tables" not in schema_config:
                schema_config["tables"] = {}

            # 构建字段配置（包含关联关系）
            fields = []
            for mapping in field_mappings:
                field_config = {
                    "name": mapping.get('targetField') or mapping.get('english_name', ''),
                    "chinese_name": mapping.get('sourceField') or mapping.get('chinese_name', ''),
                    "data_type": mapping.get('dataType') or mapping.get('data_type', 'VARCHAR'),
                    "length": mapping.get('length', 255),
                    "required": mapping.get('required', False),
                    "unique": mapping.get('unique', False),
                    "description": mapping.get('description', '')
                }

                # 添加关联关系配置
                relation_type = mapping.get('relation_type', 'none')
                if relation_type != 'none':
                    relation_config = {
                        "type": relation_type,
                        "ref_table": mapping.get('relation_table', ''),
                        "ref_field": mapping.get('relation_display_field', ''),
                        "display_field": mapping.get('relation_display_field', '')
                    }
                    field_config["relation"] = relation_config

                # 添加验证规则配置
                validation_config = {}
                if mapping.get('validation_regex'):
                    validation_config["regex"] = mapping['validation_regex']
                if mapping.get('validation_range'):
                    validation_config["range"] = mapping['validation_range']
                if validation_config:
                    field_config["validation"] = validation_config

                fields.append(field_config)

            schema_config["tables"][table_name] = {
                "chinese_name": config_name,
                "type": table_type,
                "parent_table": parent_table,
                "fields": fields,
                "updated_at": datetime.now().isoformat()
            }

            # 更新 mappings
            if "mappings" not in schema_config:
                schema_config["mappings"] = {}

            for mapping in field_mappings:
                source = mapping.get('sourceField') or mapping.get('chinese_name', '')
                target = mapping.get('targetField') or mapping.get('english_name', '')
                if source and target:
                    schema_config["mappings"][source] = {
                        "target": target,
                        "table": table_name,
                        "data_type": mapping.get('dataType') or mapping.get('data_type', 'VARCHAR')
                    }

            # 保存配置
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema_config, f, ensure_ascii=False, indent=2)

            print(f"已更新 merged_schema_mappings.json: {table_name}")

        except Exception as e:
            print(f"更新 merged_schema_mappings.json 失败: {e}")

    def _save_single_config_file(self, config: Dict[str, Any]) -> bool:
        """保存单个配置文件（向后兼容）"""
        try:
            config_name = config.get('config_name', '')
            if not config_name:
                return False

            # 构建文件路径
            safe_name = "".join(c for c in config_name if c.isalnum() or c in ('_', '-', ' ', '.'))
            safe_name = safe_name.strip()
            if not safe_name.endswith('.json'):
                safe_name += '.json'

            file_path = os.path.join(self.field_configs_dir, safe_name)

            # 构建兼容格式的配置数据
            config_data = {
                'config_name': config.get('config_name', ''),
                'display_name': config.get('config_name', ''),  # 同配置名称
                'chinese_title': config.get('config_name', ''),  # 同配置名称
                'table_name': config.get('table_name', ''),
                'table_type': config.get('table_type', 'master'),
                'parent_table': config.get('parent_table', ''),
                'field_configs': config.get('field_mappings', []),
                'created_at': config.get('created_at', ''),
                'updated_at': config.get('updated_at', '')
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"保存单个配置文件失败: {e}")
            return False

    def delete_config(self, config_id: str) -> Dict[str, Any]:
        """删除配置"""
        data = self._load_field_mappings()
        configs = data.get('configs', [])

        # 查找配置
        target_config = None
        for config in configs:
            if config.get('id') == config_id:
                target_config = config
                break

        if not target_config:
            return {'success': False, 'message': '配置不存在'}

        # 从列表中移除
        configs = [c for c in configs if c.get('id') != config_id]
        data['configs'] = configs

        # 保存
        if not self._save_field_mappings(data):
            return {'success': False, 'message': '删除配置失败'}

        # 删除单个配置文件
        config_name = target_config.get('config_name', '')
        if config_name:
            safe_name = "".join(c for c in config_name if c.isalnum() or c in ('_', '-', ' ', '.'))
            safe_name = safe_name.strip()
            if not safe_name.endswith('.json'):
                safe_name += '.json'
            file_path = os.path.join(self.field_configs_dir, safe_name)
            if os.path.exists(file_path):
                os.remove(file_path)

        return {'success': True, 'message': f'配置 "{config_name}" 已删除'}

    def get_global_mappings(self) -> Dict[str, str]:
        """获取全局字段映射"""
        data = self._load_field_mappings()
        return data.get('global_mappings', {})

    def find_matching_configs(self, filename: str) -> List[Dict[str, Any]]:
        """
        根据文件名查找匹配的配置

        Args:
            filename: 上传的文件名

        Returns:
            按匹配分数排序的配置列表
        """
        import fnmatch
        import re

        all_configs = self.get_all_configs()
        matching_configs = []

        # 提取文件名关键部分（去除扩展名）
        filename_without_ext = re.split(r'\.[^.]+$', filename)[0]

        for config in all_configs:
            pattern = config.get('source_file_pattern', '')
            config_name = config.get('config_name', '')
            table_name = config.get('table_name', '')

            match_score = 0

            # 1. 文件名模式匹配
            if pattern and fnmatch.fnmatch(filename, pattern):
                match_score += 50

                # 模式越具体，分数越高
                pattern_specificity = len([c for c in pattern if c not in '*?[]']) / len(pattern) if pattern else 0
                match_score += int(pattern_specificity * 10)

            # 2. 配置名称匹配
            if config_name:
                if filename_without_ext.lower() in config_name.lower():
                    match_score += 20
                if config_name.lower() in filename_without_ext.lower():
                    match_score += 20

            # 3. 表名匹配
            if table_name and table_name.lower() in filename_without_ext.lower():
                match_score += 15

            # 4. 最新版本加分
            if config.get('is_latest', False):
                match_score += 5

            # 5. 创建时间加分（近30天）
            try:
                created_at = datetime.fromisoformat(config.get('created_at', ''))
                days_since = (datetime.now() - created_at).days
                if days_since < 30:
                    match_score += (30 - days_since) * 0.5
            except:
                pass

            if match_score > 0:
                config_with_score = config.copy()
                config_with_score['match_score'] = int(match_score)
                matching_configs.append(config_with_score)

        # 按匹配分数排序
        matching_configs.sort(key=lambda x: x.get('match_score', 0), reverse=True)

        # 最多返回10个
        return matching_configs[:10]


# 全局实例
field_config_manager = FieldConfigManager()
