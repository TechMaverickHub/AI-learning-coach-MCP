"""
APScheduler configuration for synchronous task scheduling.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import os
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=os.getenv('SCHEDULER_TIMEZONE', 'UTC'))


def start_scheduler():
    """Initialize and start the scheduler"""
    try:
        from digest.services.digest_service import DigestService
        from rss.services.rss_service import RSSService
        
        digest_service = DigestService()
        rss_service = RSSService()
        
        def generate_daily_digest():
            return digest_service.generate_digest()
        
        def fetch_all_feeds():
            return rss_service.fetch_all_feeds()
        
        # Schedule daily digest generation at 9 AM
        scheduler.add_job(
            generate_daily_digest,
            trigger=CronTrigger(hour=9, minute=0),
            id='generate_daily_digest',
            replace_existing=True,
        )
        
        # Schedule RSS feed fetching every 6 hours
        scheduler.add_job(
            fetch_all_feeds,
            trigger=IntervalTrigger(hours=int(os.getenv('RSS_FETCH_INTERVAL_HOURS', 6))),
            id='fetch_rss_feeds',
            replace_existing=True,
        )
        
        scheduler.start()
        logger.info("APScheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

