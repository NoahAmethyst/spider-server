import time

import schedule

from job.image import upload_bing_wallpaper


def run_schedule():
    schedule.every().day.at("00:01").do(upload_bing_wallpaper)
    while True:
        schedule.run_pending()
        time.sleep(5)
