import datetime
import logging

from service.bing_daily_img import get_bing_wallpaper_cn, get_bing_wallpaper_us
from service.cos import CosCli
from util.download import download_image
from util.logger import logger


def upload_bing_wallpaper():
    cos = CosCli()
    try:
        # Upload PC CN Bing wallpaper
        cn_image_path = '/tmp/bing_wallpaper_cn.jpg'
        cn_image_url, cn_image_name = get_bing_wallpaper_cn(is_mobile=False)
        download_image(cn_image_url, cn_image_path)

        cos.upload_file('wallpaper', cn_image_name + '.jpg', cn_image_path)
    except Exception as e:
        logger.error(f'upload bing wallpaper cn failed:{e}')

    try:
        # Upload Mobile CN Bing wallpaper
        cn_image_mobile_path = '/tmp/bing_wallpaper_mobile_cn.jpg'
        cn_image_mobile_url, cn_image_name_mobile = get_bing_wallpaper_cn(is_mobile=True)
        download_image(cn_image_mobile_url, cn_image_mobile_path)

        cos.upload_file('wallpaper', cn_image_name_mobile + '_mobile.jpg', cn_image_mobile_path)
    except Exception as e:
        logger.error(f'upload bing mobile wallpaper cn failed:{e}')

        # Upload PC US Bing wallpaper
        us_image_path = '/tmp/bing_wallpaper_us.jpg'
        us_image_url, us_image_name = get_bing_wallpaper_us(is_mobile=False)
        download_image(us_image_url, us_image_path)

        cos.upload_file('wallpaper', us_image_name + '.jpg', us_image_path)
    except Exception as e:
        logger.error(f'upload bing  wallpaper us failed:{e}')

        # Upload Mobile US Bing wallpaper
    try:
        us_image_mobile_path = '/tmp/bing_wallpaper_mobile_us.jpg'
        us_image_mobile_url, us_image_name_mobile = get_bing_wallpaper_us(is_mobile=True)
        download_image(us_image_mobile_url, us_image_mobile_path)

        cos.upload_file('wallpaper', us_image_name_mobile + '_mobile.jpg', us_image_mobile_path)
    except Exception as e:
        logger.error(f'upload mobile bing  wallpaper us failed:{e}')
