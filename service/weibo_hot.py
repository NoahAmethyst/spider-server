import requests
from bs4 import BeautifulSoup

from pb import spider_pb2


def get_weibo_hot():
    cookie = 'SUB=_2AkMVWDYUf8NxqwJRmP0Sz2_hZYt2zw_EieKjBMfPJRMxHRl-yj9jqkBStRB6PtgY-38i0AF7nDAv8HdY1ZwT3Rv8B5e5; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFencmWZyNhNlrzI6f0SiqP'
    agent = 'Mozilla / 5.0(X11;Linuxx86_64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 74.0.3729.169Safari / 537.36'
    url = "https://s.weibo.com/top/summary?cate=realtimehot"
    headers = {
        "User-Agent": agent,
        "Cookie": cookie,
    }

    response = requests.get(url, headers=headers, timeout=120)

    if response.status_code != 200:
        raise Exception("Request failed with status code: ", response.status_code)

    soup = BeautifulSoup(response.content, "html.parser")

    all_data = []
    title_cache = set()
    for i, selection in enumerate(soup.select(".td-02")):
        s = selection.find("a")
        url = s.get("href")
        text = s.get_text()

        if url and "weibo" in url:
            title_cache.add(text)
            all_data.append({"title": text, "url": f"https://s.weibo.com{url}"})

    hot_list = []

    for i, data in enumerate(all_data):
        weibo_hot = spider_pb2.WeiboHot()
        weibo_hot.url = data['url']
        weibo_hot.rank = i + 1
        weibo_hot.title = data['title']
        hot_list.append(weibo_hot)

    return hot_list
