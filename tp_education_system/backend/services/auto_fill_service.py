"""
自动填报引擎
整合模板处理和数据处理，实现配置驱动的自动填报
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.template_handler import ExcelTemplateHandler, WordTemplateHandler, verify_consistency
from utils.data_processor import DataProcessor
from core.data_source_registry import data_source_registry


class AutoFillEngine:
    """自动填报引擎"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.template_handlers = {
            'xlsx': ExcelTemplateHandler,
            'xls': ExcelTemplateHandler,
            'docx': WordTemplateHandler,
            'doc': WordTemplateHandler
        }
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
        
        Returns:
            配置字典
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"[自动填报] 加载配置: {config_path}")
        return config
    
    def auto_fill(self, config: Dict[str, Any], filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行自动填报（100%复印模板）
        
        Args:
            config: 配置字典
            filters: 筛选条件（可选）
        
        Returns:
            填报结果
        """
        print("\n" + "="*50)
        print("开始自动填报")
        print("="*50)
        
        template_info = config.get('template_info', {})
        template_file = template_info.get('file')
        
        if not template_file or not os.path.exists(template_file):
            return {
                'success': False,
                'message': f"模板文件不存在: {template_file}"
            }
        
        file_ext = os.path.splitext(template_file)[1].lower().replace('.', '')
        if file_ext not in self.template_handlers:
            return {
                'success': False,
                'message': f"不支持的文件类型: .{file_ext}"
            }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{os.path.splitext(os.path.basename(template_file))[0]}_填报结果_{timestamp}.{file_ext}"
        output_path = os.path.join(os.path.dirname(template_file), 'output', output_filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        import shutil
        shutil.copy2(template_file, output_path)
        print(f"[自动填报] 复制模板: {template_file} -> {output_path}")
        
        handler_class = self.template_handlers[file_ext]
        handler = handler_class(output_path)
        
        if not handler.load():
            return {
                'success': False,
                'message': "模板加载失败"
            }
        
        data_sources = config.get('data_sources', {})
        query_config = self._build_query_config(data_sources, filters)
        
        self.data_processor.connect()
        df = self.data_processor.query_by_config(query_config)
        self.data_processor.disconnect()
        
        if df.empty:
            return {
                'success': False,
                'message': "查询数据为空"
            }
        
        field_mappings = config.get('field_mappings', [])
        df = self.data_processor.transform_dataframe(df, field_mappings)
        
        calculations = config.get('calculations', [])
        stats = self.data_processor.calculate_statistics(df, calculations)
        
        fill_data = self._prepare_fill_data(df, field_mappings, stats)
        
        if file_ext in ['xlsx', 'xls']:
            filled_wb = handler.fill_by_field_name(fill_data)
        else:
            filled_doc = handler.fill_data(fill_data)
        
        handler.export(output_path)
        
        is_consistent, consistency_msg = verify_consistency(template_file, output_path)
        
        result = {
            'success': True,
            'message': "自动填报完成",
            'output_file': output_path,
            'data_count': len(df),
            'statistics': stats,
            'consistency': {
                'is_consistent': is_consistent,
                'message': consistency_msg
            }
        }
        
        print("\n" + "="*50)
        print("自动填报完成")
        print(f"输出文件: {output_path}")
        print(f"数据量: {len(df)} 条")
        print(f"一致性: {consistency_msg}")
        print("="*50 + "\n")
        
        return result
    
    def _build_query_config(self, data_sources: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        构建查询配置
        
        Args:
            data_sources: 数据源配置
            filters: 筛选条件
        
        Returns:
            查询配置
        """
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
        
        return query_config
    
    def _prepare_fill_data(self, df, field_mappings: List[Dict[str, Any]], stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备填充数据
        
        Args:
            df: DataFrame
            field_mappings: 字段映射
            stats: 统计结果
        
        Returns:
            填充数据字典
        """
        fill_data = {}
        
        if len(df) > 0:
            first_row = df.iloc[0]
            
            for mapping in field_mappings:
                template_field = mapping.get('template_field')
                source_field = mapping.get('source_field')
                target_field = mapping.get('target_field', source_field)
                
                if source_field in df.columns:
                    fill_data[template_field] = first_row[source_field]
        
        fill_data.update(stats)
        
        return fill_data
    
    def preview_template(self, template_file: str) -> Dict[str, Any]:
        """
        预览模板
        
        Args:
            template_file: 模板文件路径
        
        Returns:
            预览结果
        """
        if not os.path.exists(template_file):
            return {
                'success': False,
                'message': f"模板文件不存在: {template_file}"
            }
        
        file_ext = os.path.splitext(template_file)[1].lower().replace('.', '')
        if file_ext not in self.template_handlers:
            return {
                'success': False,
                'message': f"不支持的文件类型: .{file_ext}"
            }
        
        handler_class = self.template_handlers[file_ext]
        handler = handler_class(template_file)
        
        if not handler.load():
            return {
                'success': False,
                'message': "模板加载失败"
            }
        
        template_info = handler.import_template()
        field_names = handler.get_all_field_names()
        
        return {
            'success': True,
            'message': "模板预览成功",
            'template_file': template_file,
            'template_info': template_info,
            'field_names': field_names,
            'preview_path': handler.preview()
        }
    
    def smart_match_fields(self, template_fields: List[str], available_tables: Optional[List[str]] = None) -> Dict[str, str]:
        """
        智能匹配字段
        
        Args:
            template_fields: 模板字段列表
            available_tables: 可用表列表（可选）
        
        Returns:
            字段匹配结果
        """
        if available_tables is None:
            available_tables = list(data_source_registry.get_all_tables().keys())
        
        matches = {}
        
        for template_field in template_fields:
            best_match = None
            best_score = 0
            
            for table_name in available_tables:
                table_info = data_source_registry.get_table(table_name)
                if not table_info:
                    continue
                
                for field_name, field_label in table_info.get('fields', {}).items():
                    score = self._calculate_similarity(template_field, field_label)
                    
                    if score > best_score:
                        best_score = score
                        best_match = f"{table_name}.{field_name}"
            
            if best_match and best_score > 0.6:
                matches[template_field] = best_match
                print(f"[智能匹配] {template_field} -> {best_match} (相似度: {best_score:.2f})")
        
        return matches
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        计算字符串相似度
        
        Args:
            str1: 字符串1
            str2: 字符串2
        
        Returns:
            相似度（0-1）
        """
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        if str1 == str2:
            return 1.0
        
        if str1 in str2 or str2 in str1:
            return 0.9
        
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio()


auto_fill_engine = AutoFillEngine()


if __name__ == '__main__':
    print("\n=== 自动填报引擎测试 ===\n")
    
    test_template = r"d:\erp_thirteen\系统说明文件类\模板\退休呈报表.xlsx"
    if os.path.exists(test_template):
        print("测试模板预览:")
        preview_result = auto_fill_engine.preview_template(test_template)
        if preview_result['success']:
            print(f"  模板文件: {preview_result['template_file']}")
            print(f"  字段数量: {len(preview_result['field_names'])}")
            print(f"  字段列表: {preview_result['field_names'][:10]}...")
        else:
            print(f"  预览失败: {preview_result['message']}")
    else:
        print(f"测试文件不存在: {test_template}")
    
    print("\n测试智能匹配:")
    template_fields = ['姓名', '身份证号', '出生日期', '性别']
    matches = auto_fill_engine.smart_match_fields(template_fields)
    print(f"  匹配结果: {matches}")
    
    print("\n测试完成!")
