import requests
from bs4 import BeautifulSoup

from pb import spider_pb2


def get_36kr_hot():
    url = "https://letschuhai.com/recent/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Upgrade-Insecure-Requests": "1",
        "Host": "letschuhai.com",
        "Referer": "https://letschuhai.com/recent",
    }

    response = requests.get(url, headers=headers, timeout=120)

    if response.status_code != 200:
        raise Exception("Request failed with status code: ", response.status_code)

    soup = BeautifulSoup(response.content, "html.parser")

    all_data = []
    for selection in soup.findAll('div', class_='css-1n5eosh'):
        # 提取链接
        link = selection.find('a')['href']
        # 提取标题
        title = selection.find('h3', class_='chakra-text css-18us435').get_text(strip=True)
        all_data.append({"title": title, "url": "https://letschuhai.com" + link})

    data = []
    for i, _data in enumerate(all_data):
        _36KrHot = spider_pb2.D36KrHot()
        _36KrHot.title = _data['title']
        _36KrHot.url = _data["url"]
        _36KrHot.rank = i + 1
        data.append(_36KrHot)

    return data
