#!/usr/bin/env python3
"""
菜单管理路由 - 以数据库为主的统一菜单管理
提供菜单备份、恢复、同步等功能
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import json
import os
import psycopg2
from datetime import datetime

router = APIRouter(prefix="/api/menu", tags=["menu"])

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
NAVIGATION_FILE = os.path.join(CONFIG_DIR, 'navigation.json')

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def read_navigation_file() -> dict:
    try:
        if os.path.exists(NAVIGATION_FILE):
            with open(NAVIGATION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"modules": []}
    except Exception as e:
        print(f"读取导航文件失败: {e}")
        return {"modules": []}


def write_navigation_file(data: dict):
    try:
        os.makedirs(os.path.dirname(NAVIGATION_FILE), exist_ok=True)
        with open(NAVIGATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"写入导航文件失败: {e}")
        return False


def sync_navigation_to_db(modules_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM navigation_modules")
        
        def insert_module(module, parent_id=None, sort_order=0):
            module_id = module.get('id')
            title = module.get('title')
            icon = module.get('icon', 'Document')
            path = module.get('path', '')
            type_ = module.get('type', 'component')
            table_name = module.get('table_name')
            api_endpoint = module.get('api_endpoint')
            component = module.get('component')
            
            cursor.execute("""
                INSERT INTO navigation_modules 
                (module_id, title, icon, path, type, parent_id, sort_order, table_name, api_endpoint, component)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (module_id, title, icon, path, type_, parent_id, sort_order, table_name, api_endpoint, component))
            
            children = module.get('children', [])
            for i, child in enumerate(children):
                insert_module(child, module_id, i)
        
        for i, module in enumerate(modules_data.get('modules', [])):
            insert_module(module, None, i)
        
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def load_navigation_from_db() -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT module_id, title, icon, path, type, parent_id, sort_order, table_name, api_endpoint, component
            FROM navigation_modules WHERE is_active = TRUE ORDER BY sort_order
        """)
        
        rows = cursor.fetchall()
        nodes = {}
        
        for row in rows:
            module_id, title, icon, path, type_, parent_id, sort_order, table_name, api_endpoint, component = row
            nodes[module_id] = {
                'id': module_id, 'title': title, 'icon': icon, 'path': path, 'type': type_,
                'parent_id': parent_id, 'sort_order': sort_order, 'children': []
            }
            if table_name:
                nodes[module_id]['table_name'] = table_name
            if api_endpoint:
                nodes[module_id]['api_endpoint'] = api_endpoint
            if component:
                nodes[module_id]['component'] = component
        
        modules = []
        for module_id, node in nodes.items():
            if node['parent_id'] is None:
                modules.append(node)
            else:
                parent = nodes.get(node['parent_id'])
                if parent:
                    parent['children'].append(node)
        
        def clean_node(node):
            if 'parent_id' in node:
                del node['parent_id']
            if 'sort_order' in node:
                del node['sort_order']
            for child in node.get('children', []):
                clean_node(child)
        
        for module in modules:
            clean_node(module)
        
        return {'modules': modules}
    finally:
        cursor.close()
        conn.close()


@router.post("/backup")
async def create_backup(data: Dict[str, Any] = Body(...)):
    name = data.get("name", f"备份_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    description = data.get("description", "")
    source = data.get("source", "manual")
    created_by = data.get("created_by")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        modules_data = read_navigation_file()
        cursor.execute("""
            INSERT INTO navigation_backups (backup_name, modules_data, source, description, created_by)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (name, json.dumps(modules_data, ensure_ascii=False), source, description, created_by))
        backup_id = cursor.fetchone()[0]
        conn.commit()
        return {"status": "success", "message": f"备份创建成功: {name}", "backup_id": backup_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"创建备份失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.get("/backups")
async def list_backups(limit: int = 50):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, backup_name, source, description, created_at, created_by
            FROM navigation_backups ORDER BY created_at DESC LIMIT %s
        """, (limit,))
        columns = ['id', 'backup_name', 'source', 'description', 'created_at', 'created_by']
        backups = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return {"status": "success", "backups": backups, "total": len(backups)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取备份列表失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.post("/restore/{backup_id}")
async def restore_backup(backup_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT modules_data, backup_name FROM navigation_backups WHERE id = %s", (backup_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"备份不存在: ID {backup_id}")
        modules_data, backup_name = result
        
        current_data = read_navigation_file()
        cursor.execute("""
            INSERT INTO navigation_backups (backup_name, modules_data, source, description)
            VALUES (%s, %s, 'restore', %s)
        """, (f"恢复前备份_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
              json.dumps(current_data, ensure_ascii=False), f"恢复{backup_name}前的自动备份"))
        
        write_navigation_file(modules_data)
        sync_navigation_to_db(modules_data)
        conn.commit()
        return {"status": "success", "message": f"已从备份 '{backup_name}' 恢复菜单"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"恢复备份失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.delete("/backup/{backup_id}")
async def delete_backup(backup_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM navigation_backups WHERE id = %s RETURNING id", (backup_id,))
        deleted = cursor.fetchone()
        conn.commit()
        if not deleted:
            raise HTTPException(status_code=404, detail=f"备份不存在: ID {backup_id}")
        return {"status": "success", "message": f"备份已删除: ID {backup_id}"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除备份失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.post("/sync/to-db")
async def sync_to_database():
    try:
        modules_data = read_navigation_file()
        sync_navigation_to_db(modules_data)
        return {"status": "success", "message": "菜单已同步到数据库"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步到数据库失败: {str(e)}")


@router.post("/sync/from-db")
async def sync_from_database():
    try:
        modules_data = load_navigation_from_db()
        write_navigation_file(modules_data)
        return {"status": "success", "message": "菜单已从数据库同步到文件"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"从数据库同步失败: {str(e)}")


@router.post("/sync/bidirectional")
async def sync_bidirectional(strategy: str = "db_first"):
    try:
        file_data = read_navigation_file()
        db_data = load_navigation_from_db()
        if strategy == "db_first":
            write_navigation_file(db_data)
            sync_navigation_to_db(db_data)
            return {"status": "success", "message": "双向同步完成（数据库优先）"}
        else:
            sync_navigation_to_db(file_data)
            return {"status": "success", "message": "双向同步完成（文件优先）"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"双向同步失败: {str(e)}")


@router.get("/modules")
async def get_modules():
    try:
        modules_data = load_navigation_from_db()
        return {"status": "success", "data": modules_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取菜单失败: {str(e)}")


@router.put("/modules")
async def update_modules(data: dict):
    try:
        write_navigation_file(data)
        sync_navigation_to_db(data)
        return {"status": "success", "message": "菜单已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新菜单失败: {str(e)}")
