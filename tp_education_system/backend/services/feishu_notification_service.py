"""
飞书通知服务
- 读取飞书应用配置，获取 tenant_access_token
- 向指定用户发送文本消息
- 供数据库备份服务调用，通知备份成功/失败状态
"""
import os
import json
import logging
import subprocess
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
FEISHU_CONFIG_FILE = os.path.join(CONFIG_DIR, 'feishu_config.json')

# 飞书 API 地址
FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
FEISHU_SEND_MSG_URL = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
FEISHU_USER_BY_EMAIL_URL = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get"


def get_feishu_config():
    """读取飞书配置"""
    if os.path.exists(FEISHU_CONFIG_FILE):
        with open(FEISHU_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def get_tenant_access_token(app_id, app_secret):
    """
    获取飞书 tenant_access_token
    返回: (token: str, error: str|None)
    """
    try:
        resp = requests.post(
            FEISHU_TOKEN_URL,
            json={"app_id": app_id, "app_secret": app_secret},
            timeout=10
        )
        data = resp.json()
        if data.get("code") == 0:
            return data.get("tenant_access_token"), None
        else:
            return None, f"获取token失败: code={data.get('code')}, msg={data.get('msg')}"
    except requests.exceptions.Timeout:
        return None, "获取飞书token超时"
    except Exception as e:
        return None, f"获取飞书token异常: {str(e)}"


def send_text_message(token, open_id, text):
    """
    发送飞书文本消息（通过 API）
    返回: (success: bool, error: str|None)
    """
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        body = {
            "receive_id": open_id,
            "msg_type": "text",
            "content": json.dumps({"text": text})
        }
        resp = requests.post(
            FEISHU_SEND_MSG_URL,
            headers=headers,
            json=body,
            timeout=10
        )
        data = resp.json()
        if data.get("code") == 0:
            return True, None
        else:
            return False, f"发送消息失败: code={data.get('code')}, msg={data.get('msg')}"
    except requests.exceptions.Timeout:
        return False, "发送飞书消息超时"
    except Exception as e:
        return False, f"发送飞书消息异常: {str(e)}"


def send_text_via_lark_cli(open_id, text):
    """
    通过 lark-cli 命令行发送飞书消息（备选方案，兼容 open_id 跨应用问题）
    返回: (success: bool, error: str|None)
    """
    try:
        # 使用 lark-cli 以 user 身份发送消息
        cmd = [
            "lark-cli", "im", "+messages-send",
            "--user-id", open_id,
            "--text", text,
            "--as", "user"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        if result.returncode == 0:
            return True, None
        else:
            return False, f"lark-cli发送失败: {result.stderr.strip() or result.stdout.strip()}"
    except subprocess.TimeoutExpired:
        return False, "lark-cli发送消息超时"
    except FileNotFoundError:
        return False, "找不到lark-cli命令"
    except Exception as e:
        return False, f"lark-cli发送异常: {str(e)}"


def get_open_id_by_email(token, email):
    """
    通过邮箱获取当前应用下的 open_id
    返回: (open_id: str, error: str|None)
    """
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {
            "user_id_type": "open_id",
            "emails": email,
        }
        resp = requests.get(
            FEISHU_USER_BY_EMAIL_URL,
            headers=headers,
            params=params,
            timeout=10
        )
        data = resp.json()
        if data.get("code") == 0:
            items = data.get("data", {}).get("items", [])
            if items:
                return items[0].get("open_id"), None
            else:
                return None, f"未找到邮箱为 {email} 的用户"
        else:
            return None, f"查询用户失败: code={data.get('code')}, msg={data.get('msg')}"
    except requests.exceptions.Timeout:
        return None, "查询用户超时"
    except Exception as e:
        return None, f"查询用户异常: {str(e)}"


def resolve_user_open_ids(token, users):
    """
    解析用户列表中的 open_id，对没有 open_id 但有邮箱的用户自动查询
    返回: 解析后的用户列表
    """
    resolved = []
    for user in users:
        name = user.get("姓名", "未知")
        open_id = user.get("open_id", "").strip()
        email = user.get("邮箱", "").strip()
        
        if not open_id and email:
            # 通过邮箱查询 open_id
            open_id, error = get_open_id_by_email(token, email)
            if error:
                logger.warning(f"无法获取用户 {name} 的 open_id ({email}): {error}")
            else:
                logger.info(f"已获取用户 {name} 的 open_id ({email}): {open_id}")
        
        if open_id:
            resolved.append({"姓名": name, "open_id": open_id})
        else:
            resolved.append({"姓名": name, "open_id": "", "error": "无法获取open_id"})
    
    return resolved


def send_backup_notification(backup_result):
    """
    向所有配置的通知用户发送备份状态通知
    backup_result: run_backup() 的返回结果字典

    返回: {"success": bool, "results": [...]}
    """
    config = get_feishu_config()
    if not config:
        logger.warning("飞书配置不存在，跳过通知")
        return {"success": True, "results": [], "skipped": True, "reason": "配置不存在"}

    if not config.get("启用通知", False):
        logger.info("飞书通知已禁用，跳过")
        return {"success": True, "results": [], "skipped": True, "reason": "通知已禁用"}

    notification_scenes = config.get("通知场景", {})

    is_success = backup_result.get("success", False)
    is_skipped = backup_result.get("skipped", False)

    if is_skipped:
        logger.info("备份被跳过，不发送通知")
        return {"success": True, "results": [], "skipped": True, "reason": "备份被跳过"}

    should_notify = False
    if is_success and notification_scenes.get("备份成功", False):
        should_notify = True
    elif not is_success and notification_scenes.get("备份失败", False):
        should_notify = True

    if not should_notify:
        logger.info("当前通知场景未启用，跳过通知")
        return {"success": True, "results": [], "skipped": True, "reason": "场景未启用"}

    app_id = config.get("App ID")
    app_secret = config.get("App Secret")
    if not app_id or not app_secret:
        logger.error("飞书应用凭证缺失")
        return {"success": False, "error": "飞书应用凭证缺失"}

    token, token_error = get_tenant_access_token(app_id, app_secret)
    if token_error:
        logger.error(f"获取飞书token失败: {token_error}")
        return {"success": False, "error": token_error}

    now = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    filename = backup_result.get("filename", "未知")
    file_size = backup_result.get("size", 0)
    size_mb = file_size / (1024 * 1024) if file_size else 0
    elapsed = backup_result.get("elapsed_seconds", 0)
    results = backup_result.get("results", [])
    failed_paths = backup_result.get("failed_paths", [])

    # 统计连续成功/失败次数
    from services.db_backup_service import get_status
    status = get_status()
    consecutive_failures = status.get("consecutive_failures", 0)
    last_success_time = status.get("last_success_time", "无记录")

    # 构建各位置状态行
    def build_location_rows():
        rows = []
        for r in results:
            label = r.get("label", "未知位置")
            if r.get("success"):
                rows.append(f"  ✅ {label}  — 成功")
            elif r.get("skipped"):
                rows.append(f"  ⏭️ {label}  — 已跳过")
            else:
                error = r.get("error", "未知错误")
                rows.append(f"  ❌ {label}  — {error}")
        return rows

    location_rows = build_location_rows()

    if is_success:
        # 成功通知
        msg_lines = [
            f"【数据库备份成功】",
            f"时间：{now}",
            f"备份文件：{filename}",
            f"文件大小：{size_mb:.2f} MB",
        ]
        if elapsed:
            msg_lines.append(f"耗时：{elapsed:.1f} 秒")
        msg_lines.append(f"────────────────────")
        msg_lines.append(f"备份结果：")
        msg_lines.extend(location_rows)
        msg_lines.append(f"────────────────────")

        # 归档清理信息
        archive_info = backup_result.get("archive_info")
        if archive_info:
            msg_lines.append(f"归档清理：{archive_info}")

        msg_lines.append(f"连续成功：{consecutive_failures} 天无失败")
        msg_lines.append(f"")
        msg_lines.append(f"—— ERP系统自动通知")
    else:
        # 失败通知
        msg_lines = [
            f"【数据库备份失败】",
            f"时间：{now}",
            f"备份文件：{filename}",
        ]
        if size_mb > 0:
            msg_lines.append(f"文件大小：{size_mb:.2f} MB")
        msg_lines.append(f"────────────────────")
        msg_lines.append(f"备份结果：")
        msg_lines.extend(location_rows)
        msg_lines.append(f"────────────────────")
        msg_lines.append(f"上次成功：{last_success_time}")
        if consecutive_failures > 0:
            msg_lines.append(f"连续失败：{consecutive_failures} 次")
        msg_lines.append(f"")
        msg_lines.append(f"请及时检查备份配置，确保数据安全！")
        msg_lines.append(f"—— ERP系统自动通知")

    message = "\n".join(msg_lines)

    # 发送给所有通知用户
    users = config.get("通知用户", [])
    notify_results = []

    for user in users:
        name = user.get("姓名", "未知")
        open_id = user.get("open_id", "").strip()
        email = user.get("邮箱", "").strip()

        if not open_id and not email:
            notify_results.append({"用户": name, "success": False, "error": "缺少open_id和邮箱"})
            continue

        success = False
        error_msg = None

        # 优先使用 API 直接发送（已有 open_id 时无需再查询）
        if open_id:
            success, error_msg = send_text_message(token, open_id, message)
            if success:
                logger.info(f"飞书通知已发送给 {name} (API)")
                notify_results.append({"用户": name, "success": True, "方式": "API"})
                continue
            else:
                logger.warning(f"API发送失败 [{name}]: {error_msg}，尝试lark-cli方式")

        # API 失败时，尝试 lark-cli
        if open_id:
            success, error_msg = send_text_via_lark_cli(open_id, message)
            if success:
                logger.info(f"飞书通知已发送给 {name} (lark-cli)")
                notify_results.append({"用户": name, "success": True, "方式": "lark-cli"})
                continue

        # 如果没有 open_id 但有邮箱，通过邮箱查 open_id 后用 API 发送
        if not open_id and email:
            api_open_id, lookup_error = get_open_id_by_email(token, email)
            if api_open_id:
                success, error_msg = send_text_message(token, api_open_id, message)
                if success:
                    logger.info(f"飞书通知已发送给 {name} (API+邮箱查询)")
                    notify_results.append({"用户": name, "success": True, "方式": "API"})
                    continue

        if not success:
            final_error = error_msg or "所有发送方式均失败"
            logger.error(f"飞书通知发送失败 [{name}]: {final_error}")
            notify_results.append({"用户": name, "success": False, "error": final_error})
    
    all_success = all(r.get("success", False) for r in notify_results)
    return {
        "success": all_success,
        "results": notify_results,
        "message": message,
    }