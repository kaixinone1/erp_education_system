#!/usr/bin/env python3
"""
管理后台路由 - 提供系统管理功能
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import json
import os
import psycopg2
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
TABLE_NAME_MAPPINGS_FILE = os.path.join(CONFIG_DIR, 'table_name_mappings.json')
MERGED_SCHEMA_FILE = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')
NAVIGATION_FILE = os.path.join(CONFIG_DIR, 'navigation.json')
FIELD_CONFIGS_DIR = os.path.join(CONFIG_DIR, 'field_configs')
FIELD_MAPPINGS_FILE = os.path.join(CONFIG_DIR, 'field_mappings.json')

# 数据库连接配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}


def read_json_file(file_path: str) -> dict:
    """读取JSON文件"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return {}


def write_json_file(file_path: str, data: dict) -> bool:
    """写入JSON文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"写入文件失败 {file_path}: {e}")
        return False


@router.post("/cleanup-table")
async def cleanup_table(data: Dict[str, Any] = Body(...)):
    """
    彻底清理表及相关配置
    删除内容：
    1. 数据库表
    2. table_name_mappings.json 中的映射
    3. merged_schema_mappings.json 中的表结构
    4. navigation.json 中的导航菜单
    5. 字段配置文件
    """
    chinese_name = data.get("chinese_name")
    english_name = data.get("english_name")

    if not chinese_name and not english_name:
        raise HTTPException(status_code=400, detail="必须提供中文表名或英文表名")

    results = {
        "database_deleted": False,
        "mapping_deleted": False,
        "schema_deleted": False,
        "navigation_deleted": False,
        "field_config_deleted": False,
        "field_mappings_deleted": False,
        "errors": []
    }

    try:
        # 1. 先查找英文表名（如果只有中文名）
        if not english_name:
            table_mappings = read_json_file(TABLE_NAME_MAPPINGS_FILE)
            mappings = table_mappings.get("mappings", {})
            if chinese_name in mappings:
                english_name = mappings[chinese_name].get("english_name")

        if not english_name:
            raise HTTPException(status_code=404, detail=f"找不到表 '{chinese_name}' 的映射信息")

        print(f"开始清理表: {chinese_name} ({english_name})")

        # 2. 删除数据库表
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()
            cursor.execute(f'DROP TABLE IF EXISTS "{english_name}" CASCADE')
            conn.commit()
            cursor.close()
            conn.close()
            results["database_deleted"] = True
            print(f"数据库表已删除: {english_name}")
        except Exception as e:
            results["errors"].append(f"删除数据库表失败: {str(e)}")
            print(f"删除数据库表失败: {e}")

        # 3. 删除 table_name_mappings.json 中的映射
        try:
            table_mappings = read_json_file(TABLE_NAME_MAPPINGS_FILE)
            if "mappings" in table_mappings and chinese_name in table_mappings["mappings"]:
                del table_mappings["mappings"][chinese_name]
            if "reverse_mappings" in table_mappings and english_name in table_mappings["reverse_mappings"]:
                del table_mappings["reverse_mappings"][english_name]
            write_json_file(TABLE_NAME_MAPPINGS_FILE, table_mappings)
            results["mapping_deleted"] = True
            print(f"表名映射已删除: {chinese_name}")
        except Exception as e:
            results["errors"].append(f"删除表名映射失败: {str(e)}")
            print(f"删除表名映射失败: {e}")

        # 4. 删除 merged_schema_mappings.json 中的表结构
        try:
            schema_config = read_json_file(MERGED_SCHEMA_FILE)
            if "tables" in schema_config and english_name in schema_config["tables"]:
                del schema_config["tables"][english_name]
            if "mappings" in schema_config:
                # 删除所有与该表相关的字段映射
                mappings_to_delete = []
                for key, value in schema_config["mappings"].items():
                    if isinstance(value, dict) and value.get("target_table") == english_name:
                        mappings_to_delete.append(key)
                    elif isinstance(value, str) and value == english_name:
                        mappings_to_delete.append(key)
                for key in mappings_to_delete:
                    del schema_config["mappings"][key]
            write_json_file(MERGED_SCHEMA_FILE, schema_config)
            results["schema_deleted"] = True
            print(f"表结构配置已删除: {english_name}")
        except Exception as e:
            results["errors"].append(f"删除表结构配置失败: {str(e)}")
            print(f"删除表结构配置失败: {e}")

        # 5. 删除 navigation.json 中的导航菜单（递归清理所有层级）
        try:
            navigation = read_json_file(NAVIGATION_FILE)
            deleted_count = 0

            def remove_from_navigation(modules):
                """递归删除导航中的表节点"""
                nonlocal deleted_count
                result = []
                for module in modules:
                    # 检查当前节点是否匹配
                    if (module.get("table_name") == english_name or
                        module.get("id") == f"table-{english_name}"):
                        deleted_count += 1
                        print(f"  删除导航节点: {module.get('title', '未知')}")
                        continue  # 跳过这个节点，不加入结果

                    # 递归处理子节点
                    if "children" in module:
                        original_count = len(module["children"])
                        module["children"] = remove_from_navigation(module["children"])
                        if len(module["children"]) < original_count:
                            print(f"  清理子菜单: {module.get('title', '未知模块')}")

                    result.append(module)
                return result

            if "modules" in navigation:
                navigation["modules"] = remove_from_navigation(navigation["modules"])

            write_json_file(NAVIGATION_FILE, navigation)
            results["navigation_deleted"] = deleted_count > 0
            print(f"导航菜单已删除: {english_name} (共删除 {deleted_count} 个节点)")
        except Exception as e:
            results["errors"].append(f"删除导航菜单失败: {str(e)}")
            print(f"删除导航菜单失败: {e}")

        # 6. 删除字段配置文件
        try:
            field_config_file = os.path.join(FIELD_CONFIGS_DIR, f"{english_name}.json")
            if os.path.exists(field_config_file):
                os.remove(field_config_file)
                results["field_config_deleted"] = True
                print(f"字段配置文件已删除: {field_config_file}")
        except Exception as e:
            results["errors"].append(f"删除字段配置文件失败: {str(e)}")
            print(f"删除字段配置文件失败: {e}")

        # 7. 删除 field_mappings.json 中的配置
        try:
            field_mappings_data = read_json_file(FIELD_MAPPINGS_FILE)
            configs = field_mappings_data.get("configs", [])
            original_count = len(configs)

            # 过滤掉与被删除表相关的配置
            field_mappings_data["configs"] = [
                config for config in configs
                if config.get("table_name") != english_name and
                   config.get("config_name") != chinese_name
            ]

            if len(field_mappings_data["configs"]) < original_count:
                write_json_file(FIELD_MAPPINGS_FILE, field_mappings_data)
                results["field_mappings_deleted"] = True
                print(f"field_mappings.json 已清理: {english_name}")
        except Exception as e:
            results["errors"].append(f"删除 field_mappings.json 配置失败: {str(e)}")
            print(f"删除 field_mappings.json 配置失败: {e}")

        return {
            "status": "success",
            "message": f"表 '{chinese_name}' ({english_name}) 已彻底清理",
            "details": results
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"清理表失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理表失败: {str(e)}")


@router.get("/tables")
async def get_all_tables():
    """获取系统中所有表的信息（包括 table_name_mappings 和 merged_schema_mappings）"""
    try:
        tables = []
        table_dict = {}  # 用于去重

        # 1. 从 table_name_mappings.json 读取
        table_mappings = read_json_file(TABLE_NAME_MAPPINGS_FILE)
        mappings = table_mappings.get("mappings", {})

        for chinese_name, info in mappings.items():
            english_name = info.get("english_name")
            if english_name and english_name not in table_dict:
                table_dict[english_name] = {
                    "chinese_name": chinese_name,
                    "english_name": english_name,
                    "table_type": info.get("table_type", "master"),
                    "created_at": info.get("created_at"),
                    "field_count": len(info.get("field_signature", []))
                }

        # 2. 从 merged_schema_mappings.json 读取（可能有没有映射的残留表）
        schema_config = read_json_file(MERGED_SCHEMA_FILE)
        schema_tables = schema_config.get("tables", {})

        for english_name, config in schema_tables.items():
            if english_name not in table_dict:
                # 这是一个在 table_name_mappings 中没有的残留表
                table_dict[english_name] = {
                    "chinese_name": config.get("chinese_name", english_name),
                    "english_name": english_name,
                    "table_type": config.get("type", "master"),
                    "created_at": config.get("updated_at", ""),
                    "field_count": len(config.get("fields", [])),
                    "is_orphan": True  # 标记为孤儿表（没有映射）
                }

        # 转换为列表
        tables = list(table_dict.values())

        return {
            "status": "success",
            "tables": tables,
            "total": len(tables)
        }
    except Exception as e:
        print(f"获取表列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取表列表失败: {str(e)}")
