from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_scheduler(app, calculator, fetcher):
    """初始化定时任务
    
    Args:
        app: Flask应用实例
        calculator: Calculator实例
        fetcher: DataFetcher实例
    """
    scheduler = BackgroundScheduler()
    
    def daily_update_job():
        """每日数据更新任务"""
        with app.app_context():
            try:
                logger.info("开始执行每日数据更新任务...")
                
                # 1. 更新自选指数数据
                from models import Index
                favorite_indices = Index.query.filter_by(is_favorite=True).all()
                
                for index in favorite_indices:
                    logger.info(f"更新指数 {index.name} ({index.code})")
                    
                    # 获取最近3天数据（防止遗漏）
                    end_date = datetime.now().strftime('%Y%m%d')
                    start_date = datetime.now().strftime('%Y%m%d')
                    
                    fetcher.fetch_index_history(index.code, start_date, end_date)
                    fetcher.fetch_index_constituents(index.code)
                
                # 2. 更新中证800数据（用于股债性价比）
                logger.info("更新中证800数据...")
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = datetime.now().strftime('%Y%m%d')
                fetcher.fetch_index_history('000906', start_date, end_date)
                
                # 3. 更新国债收益率
                logger.info("更新国债收益率...")
                fetcher.fetch_bond_yield()
                
                # 4. 更新财务数据（每季度更新一次，这里简化为每次都尝试）
                logger.info("更新财务数据...")
                fetcher.fetch_latest_financials()
                
                # 5. 执行计算
                logger.info("执行每日计算...")
                calculator.run_daily_calculation()
                
                logger.info("每日数据更新任务完成")
                
            except Exception as e:
                logger.error(f"每日数据更新任务失败: {str(e)}")
    
    # 添加定时任务：每个交易日15:30执行
    # 这里简化为每天15:30执行（实际应该判断是否为交易日）
    scheduler.add_job(
        func=daily_update_job,
        trigger=CronTrigger(hour=15, minute=30),
        id='daily_update',
        name='每日数据更新',
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    logger.info("定时任务调度器已启动")
    
    return scheduler
