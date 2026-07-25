"""
用户认证与权限管理路由
- 登录/登出
- 单位选择
- 用户管理（县级管理员管理乡镇管理员）
- 初始管理员：admin/admin
"""
import os
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import psycopg2
import psycopg2.extras

router = APIRouter(prefix="/api/auth", tags=["认证"])

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

# 简单的token存储（生产环境应使用Redis）
_active_tokens = {}

# 请求模型
class LoginRequest(BaseModel):
    用户名: str
    密码: str

class SelectUnitRequest(BaseModel):
    token: str
    单位ID: int

class CreateUserRequest(BaseModel):
    token: str
    用户名: str
    密码: str
    角色: str = 'township'  # county 或 township
    单位ID: Optional[int] = None
    权限: Optional[List[str]] = None

class UpdateUserRequest(BaseModel):
    token: str
    用户ID: int
    密码: Optional[str] = None
    角色: Optional[str] = None
    单位ID: Optional[int] = None
    权限: Optional[List[str]] = None

class ChangePasswordRequest(BaseModel):
    token: str
    旧密码: str
    新密码: str

class ResetPasswordRequest(BaseModel):
    token: str
    新密码: Optional[str] = None  # 不提供则自动生成随机密码


def _get_conn():
    return psycopg2.connect(**DB_CONFIG)


def _hash_password(password: str) -> str:
    """简单的密码哈希"""
    return hashlib.sha256(f"erp13_{password}_salt".encode()).hexdigest()


def _init_users_table():
    """初始化用户表和默认管理员"""
    conn = _get_conn()
    cursor = conn.cursor()
    try:
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'township',
                unit_id INTEGER,
                permissions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        
        # 检查是否已存在admin用户
        cursor.execute("SELECT id FROM system_users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO system_users (username, password, role, permissions) VALUES (%s, %s, %s, %s)",
                ('admin', _hash_password('admin666'), 'county', '["all"]')
            )
            conn.commit()
            print("[认证] 默认管理员已创建: admin/admin666")
    finally:
        cursor.close()
        conn.close()


def _verify_token(token: str) -> dict:
    """验证token，返回用户信息"""
    user_info = _active_tokens.get(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="未登录或token已过期")
    if user_info.get('过期时间', datetime.min) < datetime.now():
        del _active_tokens[token]
        raise HTTPException(status_code=401, detail="token已过期，请重新登录")
    return user_info


def _check_county_admin(token: str) -> dict:
    """验证县级管理员权限"""
    user_info = _verify_token(token)
    if user_info.get('角色') != 'county':
        raise HTTPException(status_code=403, detail="仅县级管理员可执行此操作")
    return user_info


# ==================== API 端点 ====================

@router.post("/login")
def login(request: LoginRequest):
    """用户登录"""
    conn = _get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute(
            "SELECT id, username, role, unit_id, permissions FROM system_users WHERE username = %s AND password = %s",
            (request.用户名, _hash_password(request.密码))
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 生成token
        token = secrets.token_hex(32)
        _active_tokens[token] = {
            '用户ID': user['id'],
            '用户名': user['username'],
            '角色': user['role'],
            '单位ID': user.get('unit_id'),
            '已选单位ID': user.get('unit_id'),
            '已选单位名称': '',
            '权限': json.loads(user.get('permissions', '[]')),
            '过期时间': datetime.now() + timedelta(hours=24)
        }
        
        return {
            "成功": True,
            "数据": {
                "token": token,
                "用户名": user['username'],
                "角色": user['role'],
                "权限": json.loads(user.get('permissions', '[]'))
            }
        }
    finally:
        cursor.close()
        conn.close()


@router.get("/units")
def get_available_units(token: str = ""):
    """获取可选单位列表（按登录角色展示对应层级）"""
    user_info = _verify_token(token)
    role = user_info.get('角色', 'township')
    
    conn = _get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        if role == 'county':
            # 县级管理员：可以看到县、镇、学校三级单位
            # 选择"县"级别 = 全县范围；选择"镇"级别 = 该镇范围；选择"学校"级别 = 该校范围
            cursor.execute("""
                SELECT id, unit_name, unit_level, parent_id, full_path, depth
                FROM unit_tree_view
                WHERE unit_level IN ('县', '镇', '学校')
                ORDER BY 
                    CASE unit_level 
                        WHEN '县' THEN 1 
                        WHEN '镇' THEN 2 
                        WHEN '学校' THEN 3 
                    END, id
            """)
        else:
            # 乡镇管理员：只能看到自己单位及下属学校
            user_unit_id = user_info.get('单位ID')
            if user_unit_id:
                cursor.execute("""
                    WITH RECURSIVE unit_tree AS (
                        SELECT id, unit_name, unit_level, parent_id, full_path, depth
                        FROM unit_tree_view WHERE id = %s
                        UNION ALL
                        SELECT u.id, u.unit_name, u.unit_level, u.parent_id, u.full_path, u.depth
                        FROM unit_tree_view u
                        INNER JOIN unit_tree t ON u.parent_id = t.id
                    )
                    SELECT * FROM unit_tree ORDER BY depth, id
                """, (user_unit_id,))
            else:
                cursor.execute("""
                    SELECT id, unit_name, unit_level, parent_id, full_path, depth
                    FROM unit_tree_view WHERE unit_level = '学校'
                    ORDER BY id
                """)
        
        units = cursor.fetchall()
        return {"成功": True, "数据": [dict(u) for u in units]}
    finally:
        cursor.close()
        conn.close()


@router.post("/select-unit")
def select_unit(request: SelectUnitRequest):
    """选择当前工作单位"""
    user_info = _verify_token(request.token)
    
    conn = _get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT unit_name, unit_level FROM unit_tree_view WHERE id = %s", (request.单位ID,))
        unit = cursor.fetchone()
        if not unit:
            raise HTTPException(status_code=404, detail="单位不存在")
        
        user_info['已选单位ID'] = request.单位ID
        user_info['已选单位名称'] = unit[0]
        _active_tokens[request.token] = user_info
        
        return {
            "成功": True,
            "数据": {
                "单位ID": request.单位ID,
                "单位名称": unit[0],
                "单位层级": unit[1]
            }
        }
    finally:
        cursor.close()
        conn.close()


@router.get("/current-unit")
def get_current_unit(token: str = ""):
    """获取当前登录用户信息及已选单位"""
    user_info = _verify_token(token)
    return {
        "成功": True,
        "数据": {
            "用户名": user_info['用户名'],
            "角色": user_info['角色'],
            "已选单位ID": user_info.get('已选单位ID'),
            "已选单位名称": user_info.get('已选单位名称', ''),
            "权限": user_info.get('权限', [])
        }
    }


@router.get("/users")
def list_users(token: str = ""):
    """列出所有用户（仅县级管理员）"""
    _check_county_admin(token)
    
    conn = _get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("""
            SELECT u.id, u.username, u.role, u.unit_id, uv.unit_name, u.permissions, u.created_at
            FROM system_users u
            LEFT JOIN unit_tree_view uv ON u.unit_id = uv.id
            ORDER BY u.role, u.id
        """)
        users = cursor.fetchall()
        return {"成功": True, "数据": [dict(u) for u in users]}
    finally:
        cursor.close()
        conn.close()


@router.post("/users")
def create_user(request: CreateUserRequest):
    """创建用户（仅县级管理员）"""
    _check_county_admin(request.token)
    
    conn = _get_conn()
    cursor = conn.cursor()
    try:
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM system_users WHERE username = %s", (request.用户名,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        permissions = json.dumps(request.权限 or [])
        cursor.execute(
            """INSERT INTO system_users (username, password, role, unit_id, permissions)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (request.用户名, _hash_password(request.密码), request.角色, request.单位ID, permissions)
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        return {"成功": True, "数据": {"用户ID": new_id, "用户名": request.用户名}}
    finally:
        cursor.close()
        conn.close()


@router.put("/users/{user_id}")
def update_user(user_id: int, request: UpdateUserRequest):
    """修改用户（仅县级管理员）"""
    _check_county_admin(request.token)
    
    conn = _get_conn()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        
        if request.密码:
            updates.append("password = %s")
            params.append(_hash_password(request.密码))
        if request.角色:
            updates.append("role = %s")
            params.append(request.角色)
        if request.单位ID is not None:
            updates.append("unit_id = %s")
            params.append(request.单位ID)
        if request.权限 is not None:
            updates.append("permissions = %s")
            params.append(json.dumps(request.权限))
        
        if updates:
            updates.append("updated_at = NOW()")
            params.append(user_id)
            cursor.execute(
                f"UPDATE system_users SET {', '.join(updates)} WHERE id = %s",
                params
            )
            conn.commit()
        
        return {"成功": True, "消息": "用户已更新"}
    finally:
        cursor.close()
        conn.close()


@router.delete("/users/{user_id}")
def delete_user(user_id: int, token: str = ""):
    """删除用户（仅县级管理员）"""
    _check_county_admin(token)
    
    conn = _get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM system_users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        if user[0] == 'admin':
            raise HTTPException(status_code=400, detail="不能删除admin管理员")
        
        cursor.execute("DELETE FROM system_users WHERE id = %s", (user_id,))
        conn.commit()
        return {"成功": True, "消息": f"用户 '{user[0]}' 已删除"}
    finally:
        cursor.close()
        conn.close()


@router.post("/logout")
def logout(token: str = ""):
    """登出"""
    _active_tokens.pop(token, None)
    return {"成功": True, "消息": "已登出"}


@router.post("/change-password")
def change_password(request: ChangePasswordRequest):
    """用户自行修改密码"""
    user_info = _verify_token(request.token)
    user_id = user_info['用户ID']
    
    conn = _get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # 验证旧密码
        cursor.execute(
            "SELECT id FROM system_users WHERE id = %s AND password = %s",
            (user_id, _hash_password(request.旧密码))
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="旧密码错误")
        
        # 验证新密码长度
        if len(request.新密码) < 6:
            raise HTTPException(status_code=400, detail="新密码长度不能少于6位")
        
        # 更新密码
        cursor.execute(
            "UPDATE system_users SET password = %s, updated_at = NOW() WHERE id = %s",
            (_hash_password(request.新密码), user_id)
        )
        conn.commit()
        return {"成功": True, "消息": "密码修改成功"}
    finally:
        cursor.close()
        conn.close()


@router.post("/users/{user_id}/reset-password")
def reset_user_password(user_id: int, request: ResetPasswordRequest):
    """县级管理员重置用户密码"""
    _check_county_admin(request.token)
    
    # 生成新密码
    import random
    import string
    if request.新密码:
        new_password = request.新密码
    else:
        # 生成8位随机密码：包含大小写字母和数字
        chars = string.ascii_letters + string.digits
        new_password = ''.join(random.choice(chars) for _ in range(8))
    
    conn = _get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # 检查用户是否存在
        cursor.execute("SELECT id, username FROM system_users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="新密码长度不能少于6位")
        
        # 更新密码
        cursor.execute(
            "UPDATE system_users SET password = %s, updated_at = NOW() WHERE id = %s",
            (_hash_password(new_password), user_id)
        )
        conn.commit()
        return {
            "成功": True, 
            "消息": f"用户 '{user['username']}' 的密码已重置",
            "数据": {"新密码": new_password}
        }
    finally:
        cursor.close()
        conn.close()


# 模块加载时初始化
_init_users_table()