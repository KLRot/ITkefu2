from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.models.models import WorkOrders, SystemSettings

async def archive_old_orders():
    """自动归档超时工单"""
    try:
        # 获取系统设置中的归档时间
        settings = await SystemSettings.get_settings()
        archive_hours = settings.archive_hours
        
        # 计算需要归档的时间点
        archive_time = datetime.now() - timedelta(hours=archive_hours)
        
        # 查找并更新需要归档的工单
        orders = await WorkOrders.filter(
            status=2,  # 已完成状态
            modified_at__lt=archive_time,  # 最后修改时间早于归档时间
            archived_at__isnull=True  # 尚未归档
        )
        
        # 批量更新状态为已归档
        archived_count = 0
        for order in orders:
            order.status = 3
            order.archived_at = datetime.now()
            await order.save()
            archived_count += 1
        
        print(f"[{datetime.now()}] 自动归档完成：归档了 {archived_count} 个工单")
    except Exception as e:
        print(f"[{datetime.now()}] 自动归档失败：{str(e)}")

def setup_archive_scheduler():
    """设置定时任务"""
    scheduler = AsyncIOScheduler()
    
    # 添加每小时执行一次的任务
    scheduler.add_job(archive_old_orders, 'interval', hours=1)
    
    # 启动调度器
    scheduler.start()
    print("工单自动归档定时任务已启动") 