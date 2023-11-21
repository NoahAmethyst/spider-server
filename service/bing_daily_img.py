import os

import requests

from service.cache import DailyCache

cache = DailyCache()


def get_bing_wallpaper_cn(is_mobile):
    k = 'cn-bing-wallpaper'
    image_url = cache.get(k)
    if image_url is not None:
        return image_url
    url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN"
    response = requests.get(url)
    return build_image_url(is_mobile, k, response)


def build_image_url(is_mobile, k, response):
    image_data = response.json()
    if is_mobile:
        image_url = "http://www.bing.com" + image_data["images"][0]["urlbase"] + '_1080x1920.jpg'
        k += '-mobile'
    else:
        image_url = "http://www.bing.com" + image_data["images"][0]["url"]
    cache.set(k, image_url)
    return image_url


def get_bing_wallpaper_us(is_mobile):
    k = 'us-bing-wallpaper'
    image_url = cache.get(k)
    if image_url is not None:
        return image_url
    remote_host = os.environ.get('REMOTE_HOST')
    if remote_host is None:
        remote_host = 'www.bing.com'
    url = f"https://{remote_host}/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    headers = {'remote': 'www.bing.com'}
    response = requests.get(url, headers=headers)
    return build_image_url(is_mobile, k, response)
