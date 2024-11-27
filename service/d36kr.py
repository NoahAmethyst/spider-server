import requests
from bs4 import BeautifulSoup

from pb import spider_pb2


def get_36kr_hot():
    url = "https://36kr.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Upgrade-Insecure-Requests": "1",
        "Host": "36kr.com",
        "Referer": "https://36kr.com/",
    }

    response = requests.get(url, headers=headers, timeout=120)

    if response.status_code != 200:
        raise Exception("Request failed with status code: ", response.status_code)

    soup = BeautifulSoup(response.content, "html.parser")

    all_data = []
    for selection in soup.select(".hotlist-item-toptwo"):
        s = selection.find("a")
        url = s.get("href")
        text = selection.select_one("a p").get_text()

        if url:
            all_data.append({"title": text, "url": "https://36kr.com" + url})

    for selection in soup.select(".hotlist-item-other-info"):
        s = selection.find("a")
        url = s.get("href")
        text = s.get_text()
        if url:
            all_data.append({"title": text, "url": "https://36kr.com" + url})

    data = []

    for i, _data in enumerate(all_data):
        _36KrHot = spider_pb2.D36KrHot()
        _36KrHot.title = _data['title']
        _36KrHot.url = _data["url"]
        _36KrHot.rank = i + 1
        data.append(_36KrHot)

    return data
