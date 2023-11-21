import datetime
from service.bing_daily_img import get_bing_wallpaper_cn, get_bing_wallpaper_us
from service.cos import CosCli
from util.download import download_image


def upload_bing_wallpaper():
    cos = CosCli()

    # Upload PC CN Bing wallpaper
    cn_image_path = '/tmp/bing_wallpaper_cn.jpeg'
    cn_image_url = get_bing_wallpaper_cn(False)
    download_image(cn_image_url, cn_image_path)

    cos.upload_file('wallpaper/Bing', f'{datetime.date.today().__str__()}-cn.jpeg', cn_image_path)

    # Upload Mobile CN Bing wallpaper
    cn_image_mobile_path = '/tmp/bing_wallpaper_mobile_cn.jpeg'
    cn_image_mobile_url = get_bing_wallpaper_cn(True)
    download_image(cn_image_mobile_url, cn_image_mobile_path)

    cos.upload_file('wallpaper/Bing', f'{datetime.date.today().__str__()}-cn-mobile.jpeg', cn_image_mobile_path)

    # Upload PC US Bing wallpaper
    us_image_path = '/tmp/bing_wallpaper_us.jpeg'
    us_image_url = get_bing_wallpaper_us(False)
    download_image(us_image_url, us_image_path)

    cos.upload_file('wallpaper/Bing', f'{datetime.date.today().__str__()}-us.jpeg', us_image_path)

    # Upload Mobile US Bing wallpaper
    us_image_mobile_path = '/tmp/bing_wallpaper_mobile_us.jpeg'
    us_image_mobile_url = get_bing_wallpaper_us(False)
    download_image(us_image_mobile_url, us_image_mobile_path)

    cos.upload_file('wallpaper/Bing', f'{datetime.date.today().__str__()}-us-mobile.jpeg', us_image_mobile_path)
