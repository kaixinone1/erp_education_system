#!/usr/bin/env python3
"""
占位符模板引擎 - 支持从中间表数据填充HTML模板
"""
import re
import os
import psycopg2
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class PlaceholderTemplateEngine:
    """占位符模板引擎"""
    
    def __init__(self, db_connection_func):
        """
        初始化模板引擎
        :param db_connection_func: 获取数据库连接的函数
        """
        self.get_db_connection = db_connection_func
    
    def get_data_from_table(self, table_name: str, field_name: str, record_id: int) -> Optional[str]:
        """从指定表的指定字段获取数据，如果没有数据返回None"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 查询数据
            query = f"SELECT {field_name} FROM {table_name} WHERE teacher_id = %s"
            cursor.execute(query, (record_id,))
            
            row = cursor.fetchone()
            if row is not None:
                # 记录存在，返回字段值（即使是None或空字符串）
                if row[0] is not None:
                    return str(row[0])
                else:
                    return None  # 字段值为NULL，返回None表示没有数据
            return None  # 记录不存在，返回None
            
        except Exception as e:
            print(f"获取数据失败: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def extract_all_placeholders_from_template(self, content: str) -> List[str]:
        """
        从模板内容中提取所有占位符（单大括号和双大括号格式）
        """
        placeholders = set()
        
        # 1. 提取被HTML标签分割的双大括号
        # 模式: <span>{</span>{字段名}<span>}</span>
        split_pattern = r'<[^>]*>\{</[^>]*>\{([^{}]+)\}<[^>]*>\}</[^>]*>'
        for match in re.findall(split_pattern, content):
            field_name = match.strip()
            if field_name and len(field_name) < 50:
                placeholders.add(field_name)
        
        # 2. 提取双大括号占位符 {{字段名}}
        double_pattern = r'\{\{([^{}]+)\}\}'
        for match in re.findall(double_pattern, content):
            field_name = match.strip()
            if field_name and len(field_name) < 50:
                placeholders.add(field_name)
        
        # 3. 提取单大括号占位符 {字段名}（过滤CSS样式）
        single_pattern = r'\{([^{}]+)\}'
        for match in re.findall(single_pattern, content):
            field_name = match.strip()
            # 过滤CSS样式
            if any(c in field_name for c in [';', '\n', '\t', 'mso-', 'font:', 'border:', 'color:', 'style:', 'background', 'padding', 'margin']):
                continue
            # 过滤包含HTML标签的
            if '<' in field_name or '>' in field_name:
                continue
            # 只保留包含中文或字母的，且长度合理的
            if field_name and len(field_name) < 50:
                if re.search(r'[\u4e00-\u9fa5a-zA-Z]', field_name):
                    placeholders.add(field_name)
        
        return list(placeholders)
    
    def normalize_template_placeholders(self, content: str) -> str:
        """
        统一模板中的所有占位符格式为 {{字段名}}
        处理各种被HTML标签分割的情况
        """
        # 获取所有占位符
        placeholders = self.extract_all_placeholders_from_template(content)
        
        for field_name in placeholders:
            # 1. 处理完整的被分割模式: <span>{</span>{字段名}<span>}</span>
            pattern_full = r'<[^>]*>\{</[^>]*>\{' + re.escape(field_name) + r'\}<[^>]*>\}</[^>]*>'
            content = re.sub(pattern_full, '{{' + field_name + '}}', content)
            
            # 2. 处理左边被分割: <span>{</span>{字段名}
            pattern_left = r'<[^>]*>\{</[^>]*>\{' + re.escape(field_name) + r'\}'
            content = re.sub(pattern_left, '{{' + field_name + '}}', content)
            
            # 3. 处理右边被分割: {字段名}<span>}</span>（后面可能有其他内容）
            pattern_right = r'\{' + re.escape(field_name) + r'\}<[^>]*>\}</[^>]*>'
            content = re.sub(pattern_right, '{{' + field_name + '}}', content)
            
            # 4. 处理单大括号格式: {字段名}（后面可能有文字如"级"）
            pattern_single = r'(?<!\{)\{' + re.escape(field_name) + r'\}(?!\})'
            content = re.sub(pattern_single, '{{' + field_name + '}}', content)
        
        return content
    
    def fill_html_template(self, template_path: str, mappings: List[Dict], 
                          record_id: int) -> str:
        """
        填充HTML模板
        """
        # 读取模板文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
        content = None
        for encoding in encodings:
            try:
                with open(template_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    break
            except:
                continue
        
        if not content:
            raise ValueError("无法读取模板文件")
        
        # 第一步：统一所有占位符格式为 {{字段名}}
        content = self.normalize_template_placeholders(content)
        
        # 第二步：构建字段映射字典
        mapping_dict = {}
        for mapping in mappings:
            placeholder = mapping['placeholder'].strip()
            # 统一格式：去掉可能的大括号
            if placeholder.startswith('{{') and placeholder.endswith('}}'):
                placeholder = placeholder[2:-2]
            elif placeholder.startswith('{') and placeholder.endswith('}'):
                placeholder = placeholder[1:-1]
            mapping_dict[placeholder] = (mapping['table'], mapping['field'])
        
        # 第三步：获取所有占位符（从已经统一格式的模板中）
        # 使用更宽松的模式，匹配 {{ 字段名 }}（包含空格）
        all_placeholders_raw = re.findall(r'\{\{([^{}]+)\}\}', content)
        all_placeholders = list(set([p.strip() for p in all_placeholders_raw]))
        
        # 第四步：获取数据并替换
        for placeholder in all_placeholders:
            if placeholder in mapping_dict:
                table, field = mapping_dict[placeholder]
                value = self.get_data_from_table(table, field, record_id)
                # 只有获取到有效数据时才替换，否则保留占位符
                if value is not None and value != '':
                    # 替换 {{占位符}} 或 {{ 占位符 }}（包含空格）为实际值
                    # 使用更宽松的模式匹配可能包含空格的占位符
                    pattern = r'\{\{\s*' + re.escape(placeholder) + r'\s*\}\}'
                    content = re.sub(pattern, value, content)
            # 如果未配置或没有数据，保留 {{占位符}} 不变
        
        return content
    
    def get_raw_template(self, template_id: str) -> str:
        """获取原始模板内容"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 先尝试用id查询（整数）
            try:
                template_id_int = int(template_id)
                cursor.execute(
                    "SELECT file_path FROM document_templates WHERE id = %s",
                    (template_id_int,)
                )
                row = cursor.fetchone()
            except ValueError:
                row = None
            
            # 如果没找到，尝试用template_id字段查询（字符串）
            if not row:
                cursor.execute(
                    "SELECT file_path FROM document_templates WHERE template_id = %s",
                    (template_id,)
                )
                row = cursor.fetchone()
            
            if not row:
                return ""
            
            file_path = row[0]
            
            # 尝试不同编码读取文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except:
                    continue
            
            return ""
            
        except Exception as e:
            print(f"获取模板失败: {e}")
            return ""
        finally:
            cursor.close()
            conn.close()
    
    def get_field_mapping(self, template_id: str) -> Dict:
        """获取字段映射配置"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 获取模板信息 - 尝试用id或template_id字段查询
            # 先尝试用id查询（整数）
            try:
                template_id_int = int(template_id)
                cursor.execute(
                    "SELECT id, file_path FROM document_templates WHERE id = %s",
                    (template_id_int,)
                )
                template_row = cursor.fetchone()
            except ValueError:
                template_row = None
            
            # 如果没找到，尝试用template_id字段查询（字符串）
            if not template_row:
                cursor.execute(
                    "SELECT id, file_path FROM document_templates WHERE template_id = %s",
                    (template_id,)
                )
                template_row = cursor.fetchone()
            
            if not template_row:
                return {'file_path': '', 'mappings': []}
            
            # 使用实际的模板ID（整数）
            actual_template_id = template_row[0]
            file_path = template_row[1]
            
            # 获取字段映射 - 使用实际的模板ID
            cursor.execute("""
                SELECT placeholder_name, intermediate_table, intermediate_field
                FROM template_field_mapping
                WHERE template_id = %s AND is_active = true
            """, (actual_template_id,))
            
            mappings = []
            for row in cursor.fetchall():
                mappings.append({
                    'placeholder': row[0],
                    'table': row[1],
                    'field': row[2]
                })
            
            return {
                'file_path': file_path,
                'mappings': mappings
            }
            
        except Exception as e:
            print(f"获取字段映射失败: {e}")
            return {'file_path': '', 'mappings': []}
        finally:
            cursor.close()
            conn.close()
    
    def generate_document(self, template_id: str, record_id: int) -> str:
        """生成文档"""
        config = self.get_field_mapping(template_id)
        
        if not config['file_path']:
            return "<p>模板不存在</p>"
        
        if not os.path.exists(config['file_path']):
            return f"<p>模板文件不存在: {config['file_path']}</p>"
        
        return self.fill_html_template(
            config['file_path'],
            config['mappings'],
            record_id
        )
