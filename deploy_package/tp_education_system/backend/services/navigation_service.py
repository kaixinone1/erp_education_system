"""
导航配置服务 - 统一管理导航节点的增删改查
"""
import json
import os
from typing import Dict, Any, List, Optional

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
NAVIGATION_FILE = os.path.join(CONFIG_DIR, 'navigation.json')


class NavigationService:
    """导航配置服务"""
    
    def __init__(self):
        self.nav_file = NAVIGATION_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """确保导航配置文件存在"""
        if not os.path.exists(self.nav_file):
            # 创建默认配置
            default_config = {
                "modules": []
            }
            os.makedirs(os.path.dirname(self.nav_file), exist_ok=True)
            with open(self.nav_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    def load_config(self) -> Dict[str, Any]:
        """加载导航配置"""
        try:
            with open(self.nav_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载导航配置失败: {e}")
            return {"modules": []}
    
    def save_config(self, config: Dict[str, Any]):
        """保存导航配置"""
        try:
            with open(self.nav_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存导航配置失败: {e}")
            return False
    
    def add_node(self, 
                 node_title: str,
                 node_path: str,
                 parent_module: str = None,
                 parent_submodule: str = None,
                 node_type: str = "table",
                 table_name: str = None,
                 component: str = None,
                 icon: str = "Document",
                 extra_props: Dict[str, Any] = None) -> bool:
        """
        添加导航节点
        
        Args:
            node_title: 节点标题（显示名称）
            node_path: 节点路径
            parent_module: 父模块名称（可选）
            parent_submodule: 父子模块名称（可选）
            node_type: 节点类型（table/component/link）
            table_name: 关联的表名（如果是数据表）
            component: 组件名称（如果是组件类型）
            icon: 图标
            extra_props: 额外属性
        """
        try:
            config = self.load_config()
            
            # 构建新节点
            new_node = {
                "id": f"node-{node_title}-{hash(node_path)}",
                "title": node_title,
                "path": node_path,
                "type": node_type,
                "icon": icon
            }
            
            # 添加额外属性
            if table_name:
                new_node["table_name"] = table_name
            if component:
                new_node["component"] = component
            if extra_props:
                new_node.update(extra_props)
            
            # 查找或创建父模块
            target_module = None
            if parent_module:
                for module in config.get('modules', []):
                    if module.get('title') == parent_module:
                        target_module = module
                        break
                
                # 如果父模块不存在，创建它
                if not target_module:
                    target_module = {
                        "id": f"module-{parent_module}",
                        "title": parent_module,
                        "icon": "Folder",
                        "children": []
                    }
                    config['modules'].append(target_module)
            else:
                # 如果没有指定父模块，使用第一个模块或创建默认模块
                if not config.get('modules'):
                    target_module = {
                        "id": "module-default",
                        "title": "数据管理",
                        "icon": "Folder",
                        "children": []
                    }
                    config['modules'].append(target_module)
                else:
                    target_module = config['modules'][0]
            
            # 查找或创建子模块
            target_submodule = None
            if parent_submodule:
                if 'children' not in target_module:
                    target_module['children'] = []
                
                for child in target_module['children']:
                    if child.get('title') == parent_submodule and child.get('type') == 'module':
                        target_submodule = child
                        break
                
                # 如果子模块不存在，创建它
                if not target_submodule:
                    target_submodule = {
                        "id": f"submodule-{parent_submodule}",
                        "title": parent_submodule,
                        "type": "module",
                        "icon": "FolderOpened",
                        "children": []
                    }
                    target_module['children'].append(target_submodule)
            
            # 确定目标容器
            if target_submodule:
                if 'children' not in target_submodule:
                    target_submodule['children'] = []
                target_container = target_submodule['children']
            else:
                if 'children' not in target_module:
                    target_module['children'] = []
                target_container = target_module['children']
            
            # 检查是否已存在同名节点
            exists = any(child.get('title') == node_title for child in target_container)
            if exists:
                print(f"导航节点已存在: {node_title}")
                return True
            
            # 添加新节点
            target_container.append(new_node)
            
            # 保存配置
            if self.save_config(config):
                print(f"导航节点添加成功: {node_title}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"添加导航节点失败: {e}")
            return False
    
    def remove_node(self, node_title: str, parent_module: str = None) -> bool:
        """删除导航节点"""
        try:
            config = self.load_config()
            
            for module in config.get('modules', []):
                if parent_module and module.get('title') != parent_module:
                    continue
                
                # 在模块的children中查找
                if 'children' in module:
                    module['children'] = [
                        child for child in module['children'] 
                        if child.get('title') != node_title
                    ]
                    
                    # 递归检查子模块
                    for child in module['children']:
                        if 'children' in child:
                            child['children'] = [
                                grandchild for grandchild in child['children']
                                if grandchild.get('title') != node_title
                            ]
            
            return self.save_config(config)
            
        except Exception as e:
            print(f"删除导航节点失败: {e}")
            return False
    
    def list_nodes(self, parent_module: str = None) -> List[Dict[str, Any]]:
        """列出所有节点"""
        config = self.load_config()
        nodes = []
        
        for module in config.get('modules', []):
            if parent_module and module.get('title') != parent_module:
                continue
            
            if 'children' in module:
                for child in module['children']:
                    nodes.append({
                        'module': module.get('title'),
                        **child
                    })
        
        return nodes


# 全局导航服务实例
navigation_service = NavigationService()


def add_navigation_node(node_title: str,
                       node_path: str,
                       parent_module: str = None,
                       parent_submodule: str = None,
                       node_type: str = "table",
                       table_name: str = None,
                       component: str = None,
                       icon: str = "Document",
                       extra_props: Dict[str, Any] = None) -> bool:
    """
    便捷函数：添加导航节点
    """
    return navigation_service.add_node(
        node_title=node_title,
        node_path=node_path,
        parent_module=parent_module,
        parent_submodule=parent_submodule,
        node_type=node_type,
        table_name=table_name,
        component=component,
        icon=icon,
        extra_props=extra_props
    )
