"""恢复 db_backup_status.json 到原始状态"""
import os
import json

STATUS_FILE = os.path.join(
    "d:", os.sep, "erp_fifteen", "tp_education_system", "backend", "config", "db_backup_status.json"
)

# 原始状态（2026-09-29 09:03:41 的备份记录）
original_status = {
    "last_backup_time": "2026-09-29 09:03:41",
    "last_backup_success": True,
    "backup_results": [
        {
            "path": "D:\\erp_fifteen\\tp_education_system\\备份\\数据库自动备份",
            "label": "位置1",
            "success": True,
            "file": "D:\\erp_fifteen\\tp_education_system\\备份\\数据库自动备份\\taiping_education_20260929_085949.sql",
            "size": 6847237,
        },
        {
            "path": "D:/erp_fifteen/备份/数据库备份_位置2",
            "label": "位置2",
            "success": True,
            "file": "D:/erp_fifteen/备份/数据库备份_位置2\\taiping_education_20260929_085949.sql",
            "size": 6847237,
        },
        {
            "path": "D:/erp_fifteen/备份/数据库备份_位置3",
            "label": "位置3",
            "success": True,
            "file": "D:/erp_fifteen/备份/数据库备份_位置3\\taiping_education_20260929_085949.sql",
            "size": 6847237,
        },
        {
            "path": "D:\\erp_fifteen\\tp_education_system",
            "label": "Git仓库",
            "success": False,
            "error": "Git推送失败（已重试3次）: fatal: unable to access 'https://github.com/kaixinone1/erp_education_system/': Failed to connect to github.com port 443 after 21068 ms: Could not connect to server。备份文件已提交到本地仓库，待网络恢复后可手动推送。",
            "skipped": False,
            "type": "git",
        },
    ],
    "failed_paths": [],
    "consecutive_failures": 0,
    "last_notification": {
        "time": "2026-09-29 09:03:43",
        "success": True,
        "skipped": False,
        "reason": "",
        "results": [
            {
                "方式": "应用API群消息",
                "success": True,
            }
        ],
        "error": "",
    },
    "last_success_time": "2026-09-29 09:03:41",
    "backup_slots": {
        "数据库自动备份": {
            "success": True,
            "time": "2026-09-29 09:03:41",
            "results": [],
            "detail": "原始备份记录（位置1/2/3成功，Git推送失败）",
        }
    },
    "overall_success": True,
}

with open(STATUS_FILE, "w", encoding="utf-8") as f:
    json.dump(original_status, f, ensure_ascii=False, indent=2)

print("OK 已恢复 db_backup_status.json 到原始状态")
print(f"  last_backup_time: {original_status['last_backup_time']}")
print(f"  last_backup_success: {original_status['last_backup_success']}")
print(f"  overall_success: {original_status['overall_success']}")
print(f"  consecutive_failures: {original_status['consecutive_failures']}")
print(f"  backup_slots keys: {list(original_status['backup_slots'].keys())}")
