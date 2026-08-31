import time

import schedule

from job.image import upload_bing_wallpaper
from job.weibo_breaking_alerts import build_weibo_breaking_alert_monitor
from util.logger import logger


def _run_weibo_monitor_safely(monitor):
    try:
        monitor.run_once()
    except Exception:
        logger.exception("Weibo breaking-alert monitor run failed")


def run_schedule():
    schedule.every().day.at("00:01").do(upload_bing_wallpaper)
    try:
        monitor = build_weibo_breaking_alert_monitor()
    except Exception:
        logger.exception("Weibo breaking-alert monitor disabled")
    else:
        _run_weibo_monitor_safely(monitor)
        schedule.every(30).minutes.do(_run_weibo_monitor_safely, monitor)
    while True:
        schedule.run_pending()
        time.sleep(5)
