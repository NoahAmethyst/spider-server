import datetime
from service.bing_daily_img import get_bing_wallpaper_cn, get_bing_wallpaper_us
from service.cos import CosCli
from util.download import download_image


def upload_bing_wallpaper():
    cos = CosCli()
    cn_image_path = '/tmp/bing_wallpaper_cn.jpeg'
    cn_image_url = get_bing_wallpaper_cn()
    download_image(cn_image_url, cn_image_path)

    cos.upload_file('wallpaper/bing', f'{datetime.date.today().__str__()}-cn.jpeg', cn_image_path)

    us_image_path = '/tmp/bing_wallpaper_us.jpeg'
    us_image_url = get_bing_wallpaper_us()
    download_image(us_image_url, us_image_path)

    cos.upload_file('wallpaper/bing', f'{datetime.date.today().__str__()}-us.jpeg', us_image_path)
