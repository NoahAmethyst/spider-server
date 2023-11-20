import requests

from service.cache import DailyCache
cache = DailyCache()


def get_bing_wallpaper_cn():
    k = 'cn-bing-wallpaper'
    image_url = cache.get(k)
    if image_url is not None:
        return image_url
    url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    response = requests.get(url)
    image_data = response.json()
    image_url = "http://www.bing.com" + image_data["images"][0]["url"]
    cache.set(k, image_url)
    return image_url


def get_bing_wallpaper_us():
    k = 'us-bing-wallpaper'
    image_url = cache.get(k)
    if image_url is not None:
        return image_url
    url = "https://remote-proxy.deno.dev/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    headers = {'remote': 'www.bing.com'}
    response = requests.get(url, headers=headers)
    image_data = response.json()
    image_url = "http://www.bing.com" + image_data["images"][0]["url"]
    cache.set(k, image_url)
    return image_url
