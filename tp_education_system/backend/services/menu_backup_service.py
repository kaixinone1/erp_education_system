"""
菜单备份机制 - 统一管理导航菜单的备份和恢复
"""
import json
import psycopg2
from datetime import datetime
from typing import Dict, Any, List, Optional

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}


def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DATABASE_CONFIG)


def init_backup_table():
    """初始化备份表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS navigation_backups (
            id SERIAL PRIMARY KEY,
            backup_name VARCHAR(200),
            modules_data JSONB NOT NULL,
            source VARCHAR(50) DEFAULT 'manual',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()


def create_backup(name: str = None, description: str = None, source: str = 'manual', created_by: str = None) -> int:
    """
    创建导航菜单备份

    Args:
        name: 备份名称（可选，默认使用时间戳）
        description: 备份描述
        source: 来源（manual/manual/auto）
        created_by: 创建人

    Returns:
        备份ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        import os
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        nav_file = os.path.join(config_dir, 'navigation.json')
        
        with open(nav_file, 'r', encoding='utf-8') as f:
            modules_data = json.load(f)
        
        if not name:
            name = f"备份_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO navigation_backups (backup_name, modules_data, source, description, created_by)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (name, json.dumps(modules_data, ensure_ascii=False), source, description, created_by))
        
        backup_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✓ 备份创建成功: {name} (ID: {backup_id})")
        return backup_id
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 创建备份失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def restore_backup(backup_id: int) -> bool:
    """
    从备份恢复导航菜单

    Args:
        backup_id: 备份ID

    Returns:
        是否成功
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT modules_data FROM navigation_backups WHERE id = %s
        """, (backup_id,))
        
        result = cursor.fetchone()
        if not result:
            print(f"✗ 备份不存在: ID {backup_id}")
            return False
        
        modules_data = result[0]
        
        import os
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        nav_file = os.path.join(config_dir, 'navigation.json')
        
        with open(nav_file, 'w', encoding='utf-8') as f:
            json.dump(modules_data, f, ensure_ascii=False, indent=2)
        
        cursor.execute("""
            INSERT INTO navigation_backups (backup_name, modules_data, source, description)
            VALUES (%s, %s, 'restore', %s)
        """, (f"恢复_{datetime.now().strftime('%Y%m%d_%H%M%S')}", json.dumps(modules_data, ensure_ascii=False), f"从ID:{backup_id}恢复"))
        
        conn.commit()
        print(f"✓ 备份恢复成功: ID {backup_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 恢复备份失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def list_backups(limit: int = 50) -> List[Dict[str, Any]]:
    """
    列出所有备份

    Args:
        limit: 返回数量限制

    Returns:
        备份列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, backup_name, source, description, created_at, created_by
            FROM navigation_backups
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        columns = ['id', 'backup_name', 'source', 'description', 'created_at', 'created_by']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    finally:
        cursor.close()
        conn.close()


def delete_backup(backup_id: int) -> bool:
    """
    删除备份

    Args:
        backup_id: 备份ID

    Returns:
        是否成功
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM navigation_backups WHERE id = %s RETURNING id", (backup_id,))
        deleted = cursor.fetchone()
        conn.commit()
        
        if deleted:
            print(f"✓ 备份已删除: ID {backup_id}")
            return True
        else:
            print(f"✗ 备份不存在: ID {backup_id}")
            return False
            
    except Exception as e:
        conn.rollback()
        print(f"✗ 删除备份失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def auto_backup_before_change() -> int:
    """
    在修改前自动创建备份（仅当天第一次修改时）

    Returns:
        备份ID或0（未创建）
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        today = datetime.now().date()
        
        cursor.execute("""
            SELECT id FROM navigation_backups
            WHERE source = 'auto' AND DATE(created_at) = %s
            LIMIT 1
        """, (today,))
        
        existing = cursor.fetchone()
        if existing:
            return 0
        
        return create_backup(
            name=f"自动备份_{today.strftime('%Y%m%d')}",
            description="系统自动备份",
            source='auto'
        )
        
    finally:
        cursor.close()
        conn.close()