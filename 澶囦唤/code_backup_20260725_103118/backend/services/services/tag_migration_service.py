"""
宽表转长表处理服务
用于将教师标签宽表转换为标准的关系表结构
"""
import pandas as pd
import psycopg2
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from datetime import datetime

# 数据库配置
DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)


def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )


def transform_wide_to_long(
    source_table: str = "raw_teacher_tags_wide",
    id_columns: List[str] = None,
    value_filter: str = "是"
) -> pd.DataFrame:
    """
    将宽表转换为长表
    
    Args:
        source_table: 源表名
        id_columns: 标识列列表（如身份证号码、姓名）
        value_filter: 只保留值等于此参数的记录
    
    Returns:
        转换后的长表DataFrame
    """
    if id_columns is None:
        id_columns = ["身份证号码", "姓名"]
    
    try:
        # 1. 从数据库读取宽表数据
        query = f"SELECT * FROM {source_table}"
        df_wide = pd.read_sql(query, engine)
        
        print(f"读取宽表数据: {len(df_wide)} 行, {len(df_wide.columns)} 列")
        
        # 2. 检查标识列是否存在
        missing_cols = [col for col in id_columns if col not in df_wide.columns]
        if missing_cols:
            raise ValueError(f"标识列不存在: {missing_cols}")
        
        # 3. 获取所有标签列（除了标识列）
        tag_columns = [col for col in df_wide.columns if col not in id_columns]
        print(f"标签列数量: {len(tag_columns)}")
        
        # 4. 使用 melt 进行逆透视
        df_long = df_wide.melt(
            id_vars=id_columns,
            var_name="标签名称",
            value_name="标签值"
        )
        
        print(f"转换后长表数据: {len(df_long)} 行")
        
        # 5. 筛选数据：只保留标签值为指定值的记录
        if value_filter:
            df_long = df_long[df_long["标签值"] == value_filter]
        
        # 6. 删除空值
        df_long = df_long.dropna(subset=["标签值"])
        
        print(f"筛选后数据: {len(df_long)} 行")
        
        return df_long
        
    except Exception as e:
        print(f"宽表转长表失败: {e}")
        raise


def get_teacher_id_by_id_card(id_card: str, teacher_table: str = "teacher_basic_info") -> Optional[int]:
    """
    根据身份证号码查询教师ID
    
    Args:
        id_card: 身份证号码
        teacher_table: 教师表名
    
    Returns:
        教师ID或None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 尝试不同的字段名
        id_card_fields = ["id_card", "身份证号码", "身份证号", "身份证"]
        
        for field in id_card_fields:
            try:
                cursor.execute(f"""
                    SELECT id FROM {teacher_table} 
                    WHERE "{field}" = %s
                    LIMIT 1
                """, (id_card,))
                
                row = cursor.fetchone()
                if row:
                    cursor.close()
                    conn.close()
                    return row[0]
            except:
                continue
        
        cursor.close()
        conn.close()
        return None
        
    except Exception as e:
        print(f"查询教师ID失败: {e}")
        return None


def get_tag_id_by_name(tag_name: str, tag_table: str = "person_tags") -> Optional[int]:
    """
    根据标签名称查询标签ID
    
    Args:
        tag_name: 标签名称
        tag_table: 标签字典表名
    
    Returns:
        标签ID或None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 尝试不同的字段名
        name_fields = ["tag_name", "标签名称", "name", "名称"]
        
        for field in name_fields:
            try:
                cursor.execute(f"""
                    SELECT id FROM {tag_table} 
                    WHERE "{field}" = %s
                    LIMIT 1
                """, (tag_name,))
                
                row = cursor.fetchone()
                if row:
                    cursor.close()
                    conn.close()
                    return row[0]
            except:
                continue
        
        cursor.close()
        conn.close()
        return None
        
    except Exception as e:
        print(f"查询标签ID失败: {e}")
        return None


# 字段名到中文标签名的映射（用于 id_card 表）
FIELD_TO_TAG_MAPPING = {
    'salary': '基础工资',
    'performance_salary': '绩效工资',
    'subsidy': '乡镇补贴',
    'post': '岗位聘用',
    'xin_ji_zhi': '新机制',
    'year_assessment': '年度考核',
    'year': '人事年报',
    'salary_year': '工资年报',
    'xiang_cun_ding_xiang': '乡村定向',
    'retired': '延迟退休',
    'party_member': '共产党员',
    'dang_ji': '党籍',
    'league_member': '共青团员',
    'tuan_ji': '团籍',
    'masses': '群众',
    'active': '在职',
    'diao_chu': '调出',
    'diao_li': '调离',
    'ci_zhi': '辞职',
    'jie_diao': '借调',
    'li_xiu': '离退',
    'retired_1': '退休',
    'si_wang': '死亡',
    'bing_xiu': '病休',
    'bing_jia': '病假',
    'zu_zhi_guan_xi_gua_kao': '组织关系挂靠'
}


def execute_tag_migration(
    source_table: str = "raw_teacher_tags_wide",
    teacher_table: str = "teacher_basic_info",
    tag_table: str = "person_tags",
    relation_table: str = "employee_tag_relations",
    id_card_column: str = "身份证号码",
    name_column: str = "姓名",
    use_field_mapping: bool = True
) -> Dict[str, Any]:
    """
    执行标签迁移：宽表转长表并写入关系表（优化版）
    
    Args:
        source_table: 源宽表名
        teacher_table: 教师主表名
        tag_table: 标签字典表名
        relation_table: 关系表名
        id_card_column: 身份证号码列名
        name_column: 姓名列名
        use_field_mapping: 是否使用字段名到标签名的映射
    
    Returns:
        迁移结果统计
    """
    result = {
        "success": False,
        "processed_count": 0,
        "success_count": 0,
        "failed_count": 0,
        "failed_records": [],
        "message": ""
    }
    
    try:
        # 1. 宽表转长表
        print("=" * 50)
        print("开始宽表转长表...")
        df_long = transform_wide_to_long(
            source_table=source_table,
            id_columns=[id_card_column, name_column]
        )
        
        if len(df_long) == 0:
            result["message"] = "没有需要迁移的数据"
            return result
        
        result["processed_count"] = len(df_long)
        
        # 2. 批量获取ID映射（优化）
        print("=" * 50)
        print("开始批量ID映射...")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 2.1 批量获取教师ID映射
        unique_id_cards = df_long[id_card_column].unique().tolist()
        print(f"唯一身份证数量: {len(unique_id_cards)}")
        
        teacher_id_map = {}
        id_card_fields = ["id_card", "身份证号码", "身份证号", "身份证"]
        
        for field in id_card_fields:
            try:
                placeholders = ','.join(['%s'] * len(unique_id_cards))
                cursor.execute(f"""
                    SELECT id, "{field}" as id_card
                    FROM {teacher_table}
                    WHERE "{field}" IN ({placeholders})
                """, tuple(unique_id_cards))
                
                for row in cursor.fetchall():
                    teacher_id_map[row[1]] = row[0]
                
                if teacher_id_map:
                    print(f"找到 {len(teacher_id_map)} 个教师ID映射")
                    break
            except Exception as e:
                print(f"字段 {field} 查询失败: {e}")
                continue
        
        # 2.2 批量获取标签ID映射
        unique_tags = df_long["标签名称"].unique().tolist()
        print(f"唯一标签数量: {len(unique_tags)}")
        
        # 如果需要，将英文字段名映射为中文标签名
        if use_field_mapping and source_table == "id_card":
            mapped_tags = []
            for tag in unique_tags:
                mapped_tag = FIELD_TO_TAG_MAPPING.get(tag, tag)
                mapped_tags.append(mapped_tag)
                print(f"  字段映射: {tag} -> {mapped_tag}")
            unique_tags = mapped_tags
            # 更新DataFrame中的标签名称
            df_long["标签名称"] = df_long["标签名称"].map(lambda x: FIELD_TO_TAG_MAPPING.get(x, x))
        
        tag_id_map = {}
        # 尝试不同的字段名（不带引号，让小写自动匹配）
        tag_field_options = [
            ("biao_qian", "biao_qian"),  # personal_dict_dictionary 表
            ("tag_name", "tag_name"),
            ("标签名称", "标签名称"),
            ("name", "name"),
            ("名称", "名称")
        ]
        
        for field_name, alias in tag_field_options:
            try:
                placeholders = ','.join(['%s'] * len(unique_tags))
                # 使用双引号包裹字段名以保留大小写
                cursor.execute(f'''
                    SELECT id, "{field_name}" as "{alias}"
                    FROM {tag_table}
                    WHERE "{field_name}" IN ({placeholders})
                ''', tuple(unique_tags))
                
                rows = cursor.fetchall()
                for row in rows:
                    tag_id_map[row[1]] = row[0]
                
                if tag_id_map:
                    print(f"使用字段 {field_name} 找到 {len(tag_id_map)} 个标签ID映射")
                    break
            except Exception as e:
                print(f"字段 {field_name} 查询失败: {e}")
                continue
        
        cursor.close()
        conn.close()
        
        # 3. 构造关系数据
        print("=" * 50)
        print("构造关系数据...")
        
        relations = []
        failed_records = []
        
        for idx, row in df_long.iterrows():
            id_card = row[id_card_column]
            tag_name = row["标签名称"]
            
            # 查找教师ID
            teacher_id = teacher_id_map.get(id_card)
            if not teacher_id:
                failed_records.append({
                    "row": int(idx),
                    "id_card": str(id_card),
                    "tag_name": str(tag_name),
                    "reason": f"未找到教师: {id_card}"
                })
                continue
            
            # 查找标签ID
            tag_id = tag_id_map.get(tag_name)
            if not tag_id:
                failed_records.append({
                    "row": int(idx),
                    "id_card": str(id_card),
                    "tag_name": str(tag_name),
                    "reason": f"未找到标签: {tag_name}"
                })
                continue
            
            # 构造关系记录
            relations.append((teacher_id, tag_id, datetime.now()))
        
        result["failed_count"] = len(failed_records)
        result["failed_records"] = failed_records[:10]  # 只保留前10条失败记录
        
        # 导出未匹配的教师到Excel
        if failed_records:
            # 筛选出"未找到教师"的记录
            unmatched_teachers = [r for r in failed_records if "未找到教师" in r.get("reason", "")]
            if unmatched_teachers:
                # 去重（同一个教师可能有多条失败记录）
                unique_unmatched = {}
                for record in unmatched_teachers:
                    id_card = record.get("id_card")
                    if id_card and id_card not in unique_unmatched:
                        unique_unmatched[id_card] = record
                
                # 获取教师姓名
                conn = get_db_connection()
                cursor = conn.cursor()
                unmatched_list = []
                for id_card, record in unique_unmatched.items():
                    try:
                        cursor.execute(f"""
                            SELECT name FROM {source_table} WHERE {id_card_column} = %s LIMIT 1
                        """, (id_card,))
                        row = cursor.fetchone()
                        name = row[0] if row else "未知"
                        unmatched_list.append({
                            "身份证号码": id_card,
                            "姓名": name,
                            "失败原因": "教师基础信息表中不存在"
                        })
                    except:
                        unmatched_list.append({
                            "身份证号码": id_card,
                            "姓名": "未知",
                            "失败原因": "教师基础信息表中不存在"
                        })
                cursor.close()
                conn.close()
                
                # 导出Excel
                if unmatched_list:
                    try:
                        import os
                        from openpyxl import Workbook
                        
                        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
                        os.makedirs(output_dir, exist_ok=True)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_file = os.path.join(output_dir, f'未匹配教师_{timestamp}.xlsx')
                        
                        wb = Workbook()
                        ws = wb.active
                        ws.title = "未匹配教师"
                        
                        # 写入表头
                        headers = ["身份证号码", "姓名", "失败原因"]
                        ws.append(headers)
                        
                        # 写入数据
                        for record in unmatched_list:
                            ws.append([record["身份证号码"], record["姓名"], record["失败原因"]])
                        
                        wb.save(output_file)
                        result["unmatched_export_file"] = output_file
                        result["unmatched_count"] = len(unmatched_list)
                        print(f"未匹配教师已导出到: {output_file}")
                    except Exception as e:
                        print(f"导出未匹配教师失败: {e}")
        
        # 4. 批量写入关系表
        print("=" * 50)
        print(f"开始批量写入 {len(relations)} 条关系...")
        
        if relations:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # 批量插入（分批处理，避免SQL过长）
                batch_size = 1000
                total_inserted = 0
                
                for i in range(0, len(relations), batch_size):
                    batch = relations[i:i + batch_size]
                    
                    insert_sql = f"""
                        INSERT INTO {relation_table} (employee_id, tag_id, created_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (employee_id, tag_id) DO NOTHING
                    """
                    
                    cursor.executemany(insert_sql, batch)
                    total_inserted += len(batch)
                    
                    if i % 1000 == 0:
                        print(f"  已处理 {total_inserted}/{len(relations)} 条...")
                
                conn.commit()
                
                result["success_count"] = total_inserted
                result["success"] = True
                result["message"] = f"成功迁移 {total_inserted} 条标签关系，失败 {len(failed_records)} 条"
                
            except Exception as e:
                conn.rollback()
                result["message"] = f"批量写入失败: {str(e)}"
            finally:
                cursor.close()
                conn.close()
        else:
            result["message"] = "没有有效的关系数据需要写入"
        
        return result
        
    except Exception as e:
        result["message"] = f"迁移失败: {str(e)}"
        return result


if __name__ == "__main__":
    # 测试代码
    print("测试宽表转长表服务...")
    
    # 测试转换
    # df = transform_wide_to_long()
    # print(df.head())
    
    # 测试完整迁移
    result = execute_tag_migration()
    print("\n迁移结果:")
    print(f"成功: {result['success']}")
    print(f"处理数量: {result['processed_count']}")
    print(f"成功数量: {result['success_count']}")
    print(f"失败数量: {result['failed_count']}")
    print(f"消息: {result['message']}")
