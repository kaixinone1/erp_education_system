"""
自动填报扩展功能服务
提供批量生成、历史记录、配置导入导出等扩展功能
"""
import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
import psycopg2

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.auto_fill_service import auto_fill_engine
from utils.data_processor import DataProcessor

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

HISTORY_TABLE = "auto_fill_history"
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config', 'template_configs')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
CUSTOM_FUNCTIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'config', 'custom_functions')

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CUSTOM_FUNCTIONS_DIR, exist_ok=True)


class AutoFillExtensionService:
    """自动填报扩展服务"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self._ensure_history_table()
    
    def _ensure_history_table(self):
        """确保历史记录表存在"""
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {HISTORY_TABLE} (
                    id SERIAL PRIMARY KEY,
                    config_name VARCHAR(255) NOT NULL,
                    template_file VARCHAR(500),
                    output_file VARCHAR(500),
                    data_count INTEGER,
                    filters JSONB,
                    statistics JSONB,
                    consistency_check BOOLEAN,
                    execution_time FLOAT,
                    status VARCHAR(50),
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100)
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"[扩展服务] 历史记录表已就绪: {HISTORY_TABLE}")
        except Exception as e:
            print(f"[扩展服务] 创建历史记录表失败: {e}")
    
    def batch_generate(self, batch_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        批量生成报表
        
        Args:
            batch_config: 批量配置
                {
                    'config_name': '退休呈报表',
                    'filter_groups': [
                        {'employment_status': '退休', 'unit': '单位A'},
                        {'employment_status': '退休', 'unit': '单位B'},
                        ...
                    ],
                    'naming_pattern': '{config_name}_{filter_value}_{timestamp}'
                }
        
        Returns:
            批量生成结果
        """
        print("\n" + "="*50)
        print("开始批量生成报表")
        print("="*50)
        
        config_name = batch_config.get('config_name')
        filter_groups = batch_config.get('filter_groups', [])
        naming_pattern = batch_config.get('naming_pattern', '{config_name}_{index}_{timestamp}')
        
        if not config_name or not filter_groups:
            return {
                'success': False,
                'message': '缺少必要参数'
            }
        
        config_path = os.path.join(CONFIG_DIR, f"{config_name}.json")
        if not os.path.exists(config_path):
            return {
                'success': False,
                'message': f'配置不存在: {config_name}'
            }
        
        results = []
        success_count = 0
        failed_count = 0
        
        for index, filters in enumerate(filter_groups):
            try:
                print(f"\n[批量生成] 正在生成第 {index + 1}/{len(filter_groups)} 个报表")
                print(f"[批量生成] 筛选条件: {filters}")
                
                config = auto_fill_engine.load_config(config_path)
                
                template_file = config.get('template_info', {}).get('file')
                if template_file and not os.path.isabs(template_file):
                    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
                    template_file = os.path.join(template_dir, os.path.basename(template_file))
                    config['template_info']['file'] = template_file
                
                result = auto_fill_engine.auto_fill(config, filters)
                
                if result['success']:
                    filter_value = '_'.join([str(v) for v in filters.values()])
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    new_filename = naming_pattern.format(
                        config_name=config_name,
                        filter_value=filter_value,
                        index=index + 1,
                        timestamp=timestamp
                    )
                    
                    old_path = result['output_file']
                    file_ext = os.path.splitext(old_path)[1]
                    new_path = os.path.join(OUTPUT_DIR, f"{new_filename}{file_ext}")
                    
                    if os.path.exists(old_path):
                        shutil.move(old_path, new_path)
                        result['output_file'] = new_path
                    
                    results.append({
                        'index': index + 1,
                        'filters': filters,
                        'success': True,
                        'output_file': result['output_file'],
                        'data_count': result['data_count']
                    })
                    success_count += 1
                else:
                    results.append({
                        'index': index + 1,
                        'filters': filters,
                        'success': False,
                        'message': result['message']
                    })
                    failed_count += 1
                
                self._save_history(
                    config_name=config_name,
                    template_file=template_file,
                    output_file=result.get('output_file', ''),
                    data_count=result.get('data_count', 0),
                    filters=filters,
                    statistics=result.get('statistics', {}),
                    consistency_check=result.get('consistency', {}).get('is_consistent', False),
                    status='success' if result['success'] else 'failed',
                    error_message=result.get('message', '')
                )
                
            except Exception as e:
                print(f"[批量生成] 第 {index + 1} 个报表生成失败: {e}")
                results.append({
                    'index': index + 1,
                    'filters': filters,
                    'success': False,
                    'message': str(e)
                })
                failed_count += 1
        
        print("\n" + "="*50)
        print("批量生成完成")
        print(f"成功: {success_count} 个")
        print(f"失败: {failed_count} 个")
        print("="*50 + "\n")
        
        return {
            'success': True,
            'message': f'批量生成完成，成功 {success_count} 个，失败 {failed_count} 个',
            'total': len(filter_groups),
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results
        }
    
    def get_history(self, limit: int = 100, config_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取历史记录
        
        Args:
            limit: 限制数量
            config_name: 配置名称（可选）
        
        Returns:
            历史记录列表
        """
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()
            
            if config_name:
                cursor.execute(f"""
                    SELECT id, config_name, template_file, output_file, data_count,
                           filters, statistics, consistency_check, execution_time,
                           status, error_message, created_at, created_by
                    FROM {HISTORY_TABLE}
                    WHERE config_name = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (config_name, limit))
            else:
                cursor.execute(f"""
                    SELECT id, config_name, template_file, output_file, data_count,
                           filters, statistics, consistency_check, execution_time,
                           status, error_message, created_at, created_by
                    FROM {HISTORY_TABLE}
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row[0],
                    'config_name': row[1],
                    'template_file': row[2],
                    'output_file': row[3],
                    'data_count': row[4],
                    'filters': row[5],
                    'statistics': row[6],
                    'consistency_check': row[7],
                    'execution_time': row[8],
                    'status': row[9],
                    'error_message': row[10],
                    'created_at': row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else '',
                    'created_by': row[12]
                })
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'history': history,
                'count': len(history)
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_statistics(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            config_name: 配置名称（可选）
        
        Returns:
            统计信息
        """
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()
            
            if config_name:
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(*) FILTER (WHERE status = 'success') as success_count,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed_count,
                        AVG(execution_time) as avg_execution_time,
                        SUM(data_count) as total_data_count
                    FROM {HISTORY_TABLE}
                    WHERE config_name = %s
                """, (config_name,))
            else:
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(*) FILTER (WHERE status = 'success') as success_count,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed_count,
                        AVG(execution_time) as avg_execution_time,
                        SUM(data_count) as total_data_count
                    FROM {HISTORY_TABLE}
                """)
            
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'statistics': {
                    'total_count': row[0] or 0,
                    'success_count': row[1] or 0,
                    'failed_count': row[2] or 0,
                    'avg_execution_time': float(row[3]) if row[3] else 0.0,
                    'total_data_count': row[4] or 0
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def _save_history(self, config_name: str, template_file: str, output_file: str,
                     data_count: int, filters: Dict[str, Any], statistics: Dict[str, Any],
                     consistency_check: bool, status: str, error_message: str = '',
                     execution_time: float = 0.0, created_by: str = 'system'):
        """保存历史记录"""
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute(f"""
                INSERT INTO {HISTORY_TABLE} 
                (config_name, template_file, output_file, data_count, filters, 
                 statistics, consistency_check, execution_time, status, 
                 error_message, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                config_name, template_file, output_file, data_count,
                json.dumps(filters, ensure_ascii=False),
                json.dumps(statistics, ensure_ascii=False),
                consistency_check, execution_time, status, error_message, created_by
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[扩展服务] 保存历史记录失败: {e}")
    
    def export_config(self, config_name: str) -> Dict[str, Any]:
        """
        导出配置
        
        Args:
            config_name: 配置名称
        
        Returns:
            导出的配置数据
        """
        try:
            config_path = os.path.join(CONFIG_DIR, f"{config_name}.json")
            
            if not os.path.exists(config_path):
                return {
                    'success': False,
                    'message': f'配置不存在: {config_name}'
                }
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            export_data = {
                'version': '1.0',
                'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'config_name': config_name,
                'config': config
            }
            
            return {
                'success': True,
                'message': '配置导出成功',
                'export_data': export_data
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def import_config(self, import_data: Dict[str, Any], overwrite: bool = False) -> Dict[str, Any]:
        """
        导入配置
        
        Args:
            import_data: 导入的配置数据
            overwrite: 是否覆盖已存在的配置
        
        Returns:
            导入结果
        """
        try:
            config_name = import_data.get('config_name')
            config = import_data.get('config')
            
            if not config_name or not config:
                return {
                    'success': False,
                    'message': '导入数据格式不正确'
                }
            
            config_path = os.path.join(CONFIG_DIR, f"{config_name}.json")
            
            if os.path.exists(config_path) and not overwrite:
                return {
                    'success': False,
                    'message': f'配置已存在: {config_name}，请使用 overwrite=True 覆盖'
                }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'message': '配置导入成功',
                'config_name': config_name,
                'config_path': config_path
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def register_custom_function(self, function_name: str, function_code: str,
                                description: str = '') -> Dict[str, Any]:
        """
        注册自定义转换函数
        
        Args:
            function_name: 函数名称
            function_code: 函数代码
            description: 函数描述
        
        Returns:
            注册结果
        """
        try:
            function_file = os.path.join(CUSTOM_FUNCTIONS_DIR, f"{function_name}.py")
            
            function_data = {
                'name': function_name,
                'code': function_code,
                'description': description,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(function_file, 'w', encoding='utf-8') as f:
                json.dump(function_data, f, ensure_ascii=False, indent=2)
            
            try:
                namespace = {}
                exec(function_code, namespace)
                if function_name in namespace:
                    self.data_processor.register_transform_function(
                        function_name, 
                        namespace[function_name]
                    )
                    return {
                        'success': True,
                        'message': '自定义函数注册成功',
                        'function_name': function_name
                    }
                else:
                    return {
                        'success': False,
                        'message': f'函数代码中未找到函数: {function_name}'
                    }
            except Exception as e:
                return {
                    'success': False,
                    'message': f'函数代码执行失败: {e}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_custom_functions(self) -> Dict[str, Any]:
        """获取所有自定义函数"""
        try:
            functions = []
            
            for filename in os.listdir(CUSTOM_FUNCTIONS_DIR):
                if filename.endswith('.py'):
                    function_file = os.path.join(CUSTOM_FUNCTIONS_DIR, filename)
                    with open(function_file, 'r', encoding='utf-8') as f:
                        function_data = json.load(f)
                        functions.append(function_data)
            
            return {
                'success': True,
                'functions': functions,
                'count': len(functions)
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def validate_data(self, config_name: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        验证数据
        
        Args:
            config_name: 配置名称
            filters: 筛选条件
        
        Returns:
            验证结果
        """
        try:
            config_path = os.path.join(CONFIG_DIR, f"{config_name}.json")
            
            if not os.path.exists(config_path):
                return {
                    'success': False,
                    'message': f'配置不存在: {config_name}'
                }
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            data_sources = config.get('data_sources', {})
            query_config = {
                'primary': data_sources.get('primary'),
                'related': data_sources.get('related', []),
                'filters': data_sources.get('filters', [])
            }
            
            if filters:
                for key, value in filters.items():
                    query_config['filters'].append({
                        'field': key,
                        'operator': '=',
                        'value': value
                    })
            
            self.data_processor.connect()
            df = self.data_processor.query_by_config(query_config)
            self.data_processor.disconnect()
            
            validations = []
            has_errors = False
            
            field_mappings = config.get('field_mappings', [])
            for mapping in field_mappings:
                source_field = mapping.get('source_field')
                template_field = mapping.get('template_field')
                
                if source_field not in df.columns:
                    validations.append({
                        'field': template_field,
                        'status': 'error',
                        'message': f'源字段不存在: {source_field}'
                    })
                    has_errors = True
                else:
                    null_count = df[source_field].isna().sum()
                    total_count = len(df)
                    
                    if null_count == total_count:
                        validations.append({
                            'field': template_field,
                            'status': 'warning',
                            'message': f'字段 {source_field} 全部为空'
                        })
                    elif null_count > 0:
                        validations.append({
                            'field': template_field,
                            'status': 'warning',
                            'message': f'字段 {source_field} 有 {null_count}/{total_count} 条空值'
                        })
                    else:
                        validations.append({
                            'field': template_field,
                            'status': 'ok',
                            'message': f'字段 {source_field} 数据完整'
                        })
            
            return {
                'success': True,
                'has_errors': has_errors,
                'data_count': len(df),
                'validations': validations,
                'can_proceed': not has_errors and len(df) > 0
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }


auto_fill_extension_service = AutoFillExtensionService()


if __name__ == '__main__':
    print("\n=== 自动填报扩展服务测试 ===\n")
    
    print("测试历史记录:")
    history_result = auto_fill_extension_service.get_history(limit=5)
    print(f"  历史记录数: {history_result.get('count', 0)}")
    
    print("\n测试统计信息:")
    stats_result = auto_fill_extension_service.get_statistics()
    if stats_result['success']:
        stats = stats_result['statistics']
        print(f"  总数: {stats['total_count']}")
        print(f"  成功: {stats['success_count']}")
        print(f"  失败: {stats['failed_count']}")
    
    print("\n测试完成!")
