import datetime
import os
import time
from urllib.parse import urlparse, parse_qs

import requests
from requests import JSONDecodeError

from service.cache import DailyCache
from util.logger import logger

cache = DailyCache()


def get_bing_wallpaper_cn(is_mobile):
    k = 'cn-bing-wallpaper'
    if is_mobile is True:
        k += '-mobile'

    image_url = cache.get(k)
    if image_url is not None:
        img_id = parse_image_id(image_url, k)
        return image_url, img_id
    url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN"
    response = requests.get(url)
    return parse_image_info(is_mobile, k, response)


def get_bing_wallpaper_us(is_mobile):
    k = 'us-bing-wallpaper'
    if is_mobile is True:
        k += '-mobile'

    image_url = cache.get(k)
    if image_url is not None:
        img_id = parse_image_id(image_url, k)
        return image_url, img_id
    remote_host = os.environ.get('REMOTE_HOST')
    if remote_host is None:
        remote_host = 'www.bing.com'
    url = f"https://{remote_host}/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    headers = {'remote': 'www.bing.com'}
    response = requests.get(url, headers=headers)
    return parse_image_info(is_mobile, k, response)


def parse_image_info(is_mobile, k, response):
    max_try = 3
    curr = 0
    try:
        image_data = response.json()
        if is_mobile is True:
            image_url = "http://www.bing.com" + image_data["images"][0]["urlbase"] + '_1080x1920.jpg'
        else:
            image_url = "http://www.bing.com" + image_data["images"][0]["url"]
        cache.set(k, image_url)
        img_id = parse_image_id(image_url, k)
        return image_url, img_id
    except JSONDecodeError as e:
        if curr > max_try:
            logger.error('Max retry time exceeded.')
        logger.error(f'parse image info failed:{e}\nGot response:{response}\nretry:{curr + 1}')
        curr += 1
        time.sleep(1)
        parse_image_info(is_mobile, k, response)


def parse_image_id(image_url, k):
    parsed_url = urlparse(image_url)
    params = parse_qs(parsed_url.query)
    img_id = params['id'][0] if 'id' in params else None
    if img_id is not None:
        if len(img_id.split('.')) > 0:
            part = img_id.split('.')[1]
            img_id = part.split('_')[0]
    else:
        img_id = f'{k}-{datetime.date.today().__str__()}'
    return img_id
