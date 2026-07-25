"""
数据源表注册中心
自动注册所有数据源表，支持后期动态扩展
"""
import psycopg2
import json
import os
from typing import Dict, Any, List, Optional

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

# 基础信息表
DATA_SOURCE_TABLES = {
    'teacher_basic_info': {
        'name': '教师基础信息',
        'description': '教师基础信息表',
        'fields': {
            'id': '主键ID',
            'name': '姓名',
            'id_card': '身份证号码',
            'gender': '性别',
            'birth_date': '出生日期',
            'nation': '民族',
            'native_place': '籍贯',
            'political_status': '政治面貌',
            'join_work_date': '参加工作时间',
            'education': '学历',
            'degree': '学位',
            'major': '专业',
            'graduate_school': '毕业院校',
            'graduate_date': '毕业时间',
            'phone': '联系电话',
            'address': '家庭住址',
            'employment_status': '任职状态',
            'unit': '所在单位',
            'created_at': '创建时间',
            'updated_at': '更新时间'
        },
        'category': '基础信息',
        'is_active': True
    },
    
    'post_appointment_info': {
        'name': '岗位聘任信息',
        'description': '教师岗位聘任信息表',
        'fields': {
            'id': '主键ID',
            'id_card': '身份证号码',
            'post': '岗位名称',
            'post_level': '岗位级别',
            'post_date': '聘任日期',
            'post_end_date': '聘任结束日期',
            'post_status': '聘任状态',
            'salary_level': '工资级别',
            'created_at': '创建时间',
            'updated_at': '更新时间'
        },
        'category': '岗位信息',
        'is_active': True
    },
    
    'teacher_personal_identity': {
        'name': '教师个人身份',
        'description': '教师个人身份信息表',
        'fields': {
            'id': '主键ID',
            'id_card': '身份证号码',
            'ge_ren_shen_fen': '个人身份',
            'is_teacher': '是否教师',
            'is_cadre': '是否干部',
            'is_worker': '是否工人',
            'created_at': '创建时间',
            'updated_at': '更新时间'
        },
        'category': '身份信息',
        'is_active': True
    }
}

# 退休相关信息表
RETIREMENT_TABLES = {
    'retirement_info': {
        'name': '退休补充信息',
        'description': '教师退休补充信息表',
        'fields': {
            'id': '主键ID',
            'id_card': '身份证号码',
            'retirement_date': '退休日期',
            'retirement_type': '退休类型',
            'retirement_reason': '退休原因',
            'pension_standard': '养老金标准',
            'pension_amount': '养老金金额',
            'retirement_unit': '退休单位',
            'created_at': '创建时间',
            'updated_at': '更新时间'
        },
        'category': '退休信息',
        'is_active': True
    },
    
    'retirement_report_data': {
        'name': '退休呈报数据',
        'description': '退休呈报表数据',
        'fields': {
            'id': '主键ID',
            'name': '姓名',
            'id_card': '身份证号码',
            'gender': '性别',
            'birth_date': '出生日期',
            'age': '年龄',
            'unit': '所在单位',
            'post': '岗位名称',
            'post_level': '岗位级别',
            'retirement_date': '退休日期',
            'retirement_type': '退休类型',
            'pension_amount': '养老金金额',
            'created_at': '创建时间',
            'updated_at': '更新时间'
        },
        'category': '退休信息',
        'is_active': True
    }
}

# 绩效工资相关表
PERFORMANCE_TABLES = {
    'performance_pay_approval': {
        'name': '绩效工资审批',
        'description': '绩效工资审批表',
        'fields': {
            'id': '主键ID',
            'year_month': '年月',
            'name': '姓名',
            'id_card': '身份证号码',
            'unit': '所在单位',
            'post': '岗位名称',
            'performance_amount': '绩效工资',
            'subsidy_amount': '补贴金额',
            'total_amount': '总金额',
            'status': '审批状态',
            'created_at': '创建时间',
            'updated_at': '更新时间'
        },
        'category': '绩效工资',
        'is_active': True
    },
    
    'performance_pay_standards': {
        'name': '绩效工资标准',
        'description': '绩效工资标准表',
        'fields': {
            'id': '主键ID',
            'post_level': '岗位级别',
            'performance_standard': '绩效标准',
            'subsidy_standard': '补贴标准',
            'effective_date': '生效日期',
            'created_at': '创建时间',
            'updated_at': '更新时间'
        },
        'category': '绩效工资',
        'is_active': True
    }
}

# 字典表
DICTIONARY_TABLES = {
    'dict_dictionary': {
        'name': '任职状态字典',
        'description': '教师任职状态字典表',
        'fields': {
            'id': '主键ID',
            'employment_status': '任职状态',
            'status_code': '状态代码',
            'sort_order_sequence': '排序序号',
            'shi_fou_you_xiao': '是否有效'
        },
        'category': '字典',
        'is_dict': True,
        'is_active': True
    },
    
    'dict_dictionary_personal': {
        'name': '岗位名称字典',
        'description': '教师岗位名称字典表',
        'fields': {
            'id': '主键ID',
            'post': '岗位名称',
            'post_code': '岗位代码',
            'sort_order_sequence': '排序序号',
            'shi_fou_you_xiao': '是否有效'
        },
        'category': '字典',
        'is_dict': True,
        'is_active': True
    },
    
    'dict_education_level_dictionary': {
        'name': '学历字典',
        'description': '学历层次字典表',
        'fields': {
            'id': '主键ID',
            'education': '学历',
            'education_code': '学历代码',
            'sort_order_sequence': '排序序号'
        },
        'category': '字典',
        'is_dict': True,
        'is_active': True
    },
    
    'dict_unit_dictionary': {
        'name': '单位字典',
        'description': '学校单位字典表',
        'fields': {
            'id': '主键ID',
            'unit': '单位名称',
            'unit_code': '单位代码',
            'sort_order_sequence': '排序序号'
        },
        'category': '字典',
        'is_dict': True,
        'is_active': True
    }
}

# 其他业务表
OTHER_TABLES = {
    'teacher_education_record': {
        'name': '教师学历记录',
        'description': '教师学历教育记录表',
        'fields': {
            'id': '主键ID',
            'id_card': '身份证号码',
            'education': '学历',
            'degree': '学位',
            'major': '专业',
            'graduate_school': '毕业院校',
            'graduate_date': '毕业时间',
            'education_type': '学历类型'
        },
        'category': '教育信息',
        'is_active': True
    },
    
    'teacher_certificate_info': {
        'name': '教师资格信息',
        'description': '教师资格证信息表',
        'fields': {
            'id': '主键ID',
            'id_card': '身份证号码',
            'certificate_type': '资格证类型',
            'certificate_no': '资格证编号',
            'certificate_date': '取得日期',
            'certificate_level': '资格证级别'
        },
        'category': '资格信息',
        'is_active': True
    },
    
    'salary_data': {
        'name': '工资数据',
        'description': '教师工资数据表',
        'fields': {
            'id': '主键ID',
            'id_card': '身份证号码',
            'year_month': '年月',
            'basic_salary': '基本工资',
            'performance_salary': '绩效工资',
            'subsidy': '补贴',
            'total_salary': '总工资'
        },
        'category': '工资信息',
        'is_active': True
    }
}


class DataSourceRegistry:
    """数据源表注册中心"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.tables: Dict[str, Dict[str, Any]] = {}
        self._register_all_tables()
        self._initialized = True
        print(f"[数据源注册] 已注册 {len(self.tables)} 个数据源表")
    
    def _register_all_tables(self):
        """注册所有数据源表"""
        for table_name, table_info in DATA_SOURCE_TABLES.items():
            self.tables[table_name] = table_info
        
        for table_name, table_info in RETIREMENT_TABLES.items():
            self.tables[table_name] = table_info
        
        for table_name, table_info in PERFORMANCE_TABLES.items():
            self.tables[table_name] = table_info
        
        for table_name, table_info in DICTIONARY_TABLES.items():
            self.tables[table_name] = table_info
        
        for table_name, table_info in OTHER_TABLES.items():
            self.tables[table_name] = table_info
        
        self._load_database_tables()
    
    def _load_database_tables(self):
        """从数据库加载所有表"""
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            for row in cursor.fetchall():
                table_name = row[0]
                if table_name not in self.tables:
                    self.tables[table_name] = {
                        'name': table_name,
                        'description': f'{table_name}表',
                        'fields': self._get_table_fields(cursor, table_name),
                        'category': '其他',
                        'is_active': True
                    }
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[数据源注册] 从数据库加载表失败: {e}")
    
    def _get_table_fields(self, cursor, table_name: str) -> Dict[str, str]:
        """获取表的字段信息"""
        try:
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (table_name,))
            
            fields = {}
            for row in cursor.fetchall():
                fields[row[0]] = row[0]
            
            return fields
        except:
            return {}
    
    def get_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        """获取表信息"""
        return self.tables.get(table_name)
    
    def get_all_tables(self) -> Dict[str, Dict[str, Any]]:
        """获取所有表"""
        return self.tables
    
    def get_tables_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """按类别获取表"""
        return {
            name: info 
            for name, info in self.tables.items() 
            if info.get('category') == category
        }
    
    def get_categories(self) -> List[str]:
        """获取所有类别"""
        categories = set()
        for info in self.tables.values():
            categories.add(info.get('category', '其他'))
        return sorted(list(categories))
    
    def register_table(self, table_name: str, table_info: Dict[str, Any]):
        """手动注册新表"""
        self.tables[table_name] = table_info
        print(f"[数据源注册] 手动注册表: {table_name}")
    
    def to_json(self) -> str:
        """导出为JSON"""
        return json.dumps(self.tables, ensure_ascii=False, indent=2)
    
    def save_to_file(self, file_path: str):
        """保存到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        print(f"[数据源注册] 已保存到: {file_path}")


data_source_registry = DataSourceRegistry()


if __name__ == '__main__':
    print("\n=== 数据源表注册中心测试 ===\n")
    
    print(f"总表数: {len(data_source_registry.get_all_tables())}")
    
    print(f"\n类别列表: {data_source_registry.get_categories()}")
    
    for category in data_source_registry.get_categories():
        tables = data_source_registry.get_tables_by_category(category)
        print(f"\n{category} ({len(tables)}个表):")
        for table_name, table_info in tables.items():
            print(f"  - {table_name}: {table_info['name']}")
    
    config_file = os.path.join(os.path.dirname(__file__), 'data_source_tables.json')
    data_source_registry.save_to_file(config_file)
