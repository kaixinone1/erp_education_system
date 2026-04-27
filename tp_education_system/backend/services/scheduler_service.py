"""
定时任务调度模块
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def setup_scheduled_tasks():
    """设置定时任务"""
    
    # 触发条件监听任务 - 每5分钟检测一次
    try:
        from services.trigger_monitor import run_trigger_monitor
        
        scheduler.add_job(
            run_trigger_monitor,
            trigger=IntervalTrigger(minutes=5),
            id='trigger_monitor',
            name='触发条件监听',
            replace_existing=True
        )
        logger.info("[OK] 触发条件监听任务已注册 (每5分钟)")
    except Exception as e:
        logger.error(f"[ERROR] 注册触发条件监听任务失败: {e}")

    # 待办到期检查任务 - 每天2点检查
    try:
        from services.todo_reminder import check_deadline_todos
        
        scheduler.add_job(
            check_deadline_todos,
            trigger='cron',
            hour=2,
            minute=0,
            id='todo_deadline_check',
            name='待办到期检查',
            replace_existing=True
        )
        logger.info("[OK] 待办到期检查任务已注册 (每天2:00)")
    except Exception as e:
        logger.error(f"[ERROR] 注册待办到期检查任务失败: {e}")

    # 待办历史归档任务 - 每天3点检查
    try:
        from services.todo_reminder import archive_completed_todos
        
        scheduler.add_job(
            archive_completed_todos,
            trigger='cron',
            hour=3,
            minute=0,
            id='todo_archive',
            name='待办历史归档',
            replace_existing=True
        )
        logger.info("[OK] 待办历史归档任务已注册 (每天3:00)")
    except Exception as e:
        logger.error(f"[ERROR] 注册待办历史归档任务失败: {e}")

    # 到龄退休提醒任务 - 每天2点检查
    try:
        from utils.todo_scheduler import scan_retirement_reminder
        
        scheduler.add_job(
            scan_retirement_reminder,
            trigger='cron',
            hour=2,
            minute=30,
            id='retirement_reminder_scan',
            name='到龄退休提醒扫描',
            replace_existing=True
        )
        logger.info("[OK] 到龄退休提醒扫描任务已注册 (每天2:30)")
    except Exception as e:
        logger.error(f"[ERROR] 注册到龄退休提醒扫描任务失败: {e}")

    # 80周岁高龄补贴提醒任务 - 每天2点检查
    try:
        from utils.todo_scheduler import scan_octogenarian_subsidy
        
        scheduler.add_job(
            scan_octogenarian_subsidy,
            trigger='cron',
            hour=2,
            minute=30,
            id='octogenarian_scan',
            name='80周岁高龄补贴扫描',
            replace_existing=True
        )
        logger.info("[OK] 80周岁高龄补贴扫描任务已注册 (每天2:30)")
    except Exception as e:
        logger.error(f"[ERROR] 注册80周岁高龄补贴扫描任务失败: {e}")


def start_scheduler():
    """启动定时任务"""
    if not scheduler.running:
        setup_scheduled_tasks()
        scheduler.start()
        logger.info("[OK] 定时任务调度器已启动")
    else:
        logger.info("[INFO] 定时任务调度器已在运行中")


def stop_scheduler():
    """停止定时任务"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("[OK] 定时任务调度器已停止")
