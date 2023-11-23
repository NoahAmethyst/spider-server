import requests
from bs4 import BeautifulSoup

from pb.spider_pb2 import WallStreetNew


def get_wallstreet_news():
    url = "https://wallstreetcn.com/news/global"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Upgrade-Insecure-Requests": "1",
    }

    response = requests.get(url, headers=headers, timeout=120)

    if response.status_code != 200:
        raise Exception("Request failed with status code: ", response.status_code)

    soup = BeautifulSoup(response.content, "html.parser")

    all_data = []
    for selection in soup.select(".article-entry"):
        s = selection.find("a")
        url = s.get("href")
        text = selection.find("span").text
        content = None
        _content = selection.find('div', class_="content")
        if _content is not None:
            content = _content.text

        if url:
            all_data.append({"title": text, "content": content, "url": url})

    data = []

    for i, _data in enumerate(all_data):
        wallStreetNew = WallStreetNew()
        wallStreetNew.title = _data['title']
        wallStreetNew.content = _data['content']
        wallStreetNew.url = _data['url']

        data.append(wallStreetNew)

    return data
