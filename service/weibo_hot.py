import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from pb import spider_pb2


WEIBO_TOP_URL = "https://s.weibo.com/top/summary?cate=recommend"
WEIBO_BASE_URL = "https://s.weibo.com"
REQUEST_TIMEOUT_SECONDS = 20
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/138.0.0.0 Safari/537.36"
)


def parse_weibo_hot_html(content: bytes) -> list[spider_pb2.WeiboHot]:
    soup = BeautifulSoup(content, "html.parser")
    hot_list = []

    for row in soup.select("tr"):
        rank_cell = row.select_one(".td-01")
        content_cell = row.select_one(".td-02")
        link = content_cell.find("a", href=True) if content_cell else None
        rank_text = rank_cell.get_text(strip=True) if rank_cell else ""

        if not (link and rank_text.isdigit()):
            continue

        heat = 0
        for span in reversed(content_cell.find_all("span")):
            value = span.get_text(strip=True).replace(",", "")
            if value.isdigit():
                heat = int(value)
                break

        item = spider_pb2.WeiboHot(
            title=link.get_text(strip=True),
            url=urljoin(WEIBO_BASE_URL, link["href"]),
            hot=heat,
            rank=int(rank_text),
        )
        item.tags.extend(
            tag.get_text(strip=True)
            for tag in content_cell.select(".icon-txt")
            if tag.get_text(strip=True)
        )
        hot_list.append(item)

    if not hot_list:
        raise ValueError("Weibo hot-list HTML contains no ranking rows")

    return hot_list


def get_weibo_hot():
    headers = {"User-Agent": USER_AGENT}
    cookie = os.getenv("WEIBO_COOKIE")
    if cookie:
        headers["Cookie"] = cookie

    response = requests.get(
        WEIBO_TOP_URL,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return parse_weibo_hot_html(response.content)
