import datetime
import os
import time
from urllib.parse import urlparse, parse_qs

import requests

from service.cache import DailyCache
from util.logger import logger

cache = DailyCache()
_BING_HOST = "www.bing.com"
_MAX_REQUEST_ATTEMPTS = 3
_REQUEST_TIMEOUT_SECONDS = 15


def get_bing_wallpaper_cn(is_mobile):
    k = 'cn-bing-wallpaper'
    if is_mobile is True:
        k += '-mobile'

    image_url = cache.get(k)
    if image_url is not None:
        img_id = parse_image_id(image_url, k)
        return image_url, img_id
    url = f"https://{_BING_HOST}/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN"
    return _request_image_info(is_mobile, k, [(url, None)])


def get_bing_wallpaper_us(is_mobile):
    k = 'us-bing-wallpaper'
    if is_mobile is True:
        k += '-mobile'

    image_url = cache.get(k)
    if image_url is not None:
        img_id = parse_image_id(image_url, k)
        return image_url, img_id
    remote_host = os.environ.get('REMOTE_HOST') or _BING_HOST
    remote_url = f"https://{remote_host}/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    request_targets = [(remote_url, {'remote': _BING_HOST})]
    if remote_host != _BING_HOST:
        official_url = f"https://{_BING_HOST}/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
        request_targets.append((official_url, None))
    return _request_image_info(is_mobile, k, request_targets)


def _request_image_info(is_mobile, k, request_targets):
    for attempt in range(1, _MAX_REQUEST_ATTEMPTS + 1):
        target_index = min(attempt - 1, len(request_targets) - 1)
        url, headers = request_targets[target_index]
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=_REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return parse_image_info(is_mobile, k, response)
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as error:
            if attempt == _MAX_REQUEST_ATTEMPTS:
                logger.error(
                    f'fetch Bing image failed after {attempt} attempts: {error}'
                )
                raise
            logger.warning(
                f'fetch Bing image failed: {error}; '
                f'retrying {attempt + 1}/{_MAX_REQUEST_ATTEMPTS}'
            )
            time.sleep(1)


def parse_image_info(is_mobile, k, response):
    image_data = response.json()
    if is_mobile is True:
        image_url = "http://www.bing.com" + image_data["images"][0]["urlbase"] + '_1080x1920.jpg'
    else:
        image_url = "http://www.bing.com" + image_data["images"][0]["url"]
    cache.set(k, image_url)
    img_id = parse_image_id(image_url, k)
    return image_url, img_id


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
