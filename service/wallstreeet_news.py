from optparse import Option

import requests
from bs4 import BeautifulSoup
from pb.spider_pb2 import WallStreetNew
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from dataclasses_json import DataClassJsonMixin, config


@dataclass
class Author:
    avatar: Optional[str] = field(default=None)
    display_name: Optional[str] = field(default=None)
    uri: Optional[str] = field(default=None)
    id: Optional[int] = field(default=None)


@dataclass
class Category:
    property_key: Optional[str] = field(default=None)
    property_name: Optional[str] = field(default=None)


@dataclass
class ContentArg:
    class_: Optional[str] = field(metadata=config(field_name="class"))
    height: Optional[str] = field(default=None)
    placeholder: Optional[str] = field(default=None)
    src: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None)
    width: Optional[str] = field(default=None)


@dataclass
class Image:
    uri: Optional[str] = field(default=None)
    height: Optional[int] = field(default=None)
    width: Optional[int] = field(default=None)
    size: Optional[int] = field(default=None)


@dataclass
class RelatedTheme:
    description: Optional[str] = field(default=None)
    image_uri: Optional[str] = field(default=None)
    is_followed: Optional[bool] = field(default=False)
    is_priced: Optional[bool] = field(default=False)
    key: Optional[str] = field(default=None)
    title: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None)
    uri: Optional[str] = field(default=None)
    id: Optional[int] = field(default=None)


@dataclass
class Article:
    title: Optional[str] = field(default=None)
    content_short: Optional[str] = field(default=None)
    uri: Optional[str] = field(default=None)
    comment_count: Optional[int] = field(default=None)
    pageviews: Optional[int] = field(default=None)
    image: Optional[Image] = field(default=None)
    display_time: Optional[int] = field(default=None)
    is_global_carousel: Optional[bool] = field(default=False)
    symbols: Optional[List[str]] = field(default=None)
    tags: Optional[List[str]] = field(default=None)
    author: Optional[Author] = field(default=None)
    id: Optional[int] = field(default=None)


@dataclass
class Resource:
    id: Optional[int] = field(default=None)
    is_paid: Optional[bool] = field(default=False)
    is_priced: Optional[bool] = field(default=False)
    is_trial: Optional[bool] = field(default=False)
    layout: Optional[str] = field(default=None)
    limited_time: Optional[int] = field(default=None)
    source_name: Optional[str] = field(default=None)
    source_uri: Optional[str] = field(default=None)
    subtitle: Optional[str] = field(default=None)
    title: Optional[str] = field(default=None)
    uri: Optional[str] = field(default=None)
    vip_type: Optional[str] = field(default=None)
    author: Optional[Author] = field(default=None)
    related_themes: Optional[List[RelatedTheme]] = field(default=None)
    hang_down: Optional[Dict] = field(default=None)
    categories: Optional[List[Category]] = field(default=None)
    content_args: Optional[List[ContentArg]] = field(default=None)
    content_short: Optional[str] = field(default=None)
    display_time: Optional[int] = field(default=None)
    image: Optional[Image] = field(default=None)
    is_in_vip_privilege: Optional[bool] = field(default=False)
    is_istio_api: Optional[bool] = field(default=False)


@dataclass
class Item:
    resource_type: Optional[str]
    resource_owner: Optional[str]
    resource: Optional[Resource]


@dataclass
class Data:
    next_cursor: Optional[str]
    is_inhouse: Optional[bool]
    item_count: Optional[int]
    items: Optional[List[Item]]


@dataclass
class Response:
    code: Optional[int]
    message: Optional[str]
    data: Optional[Data]


@dataclass
class ResponseWithJSON(Response, DataClassJsonMixin):
    pass


@dataclass
class WallStreetSort:
    title: str
    content: str
    url: str
    display_time: int


def _get_wallstreet_news():
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


def get_wallstreet_news():
    url = "https://api-one-wscn.awtmt.com/apiv1/content/information-flow?channel=global&accept=article&cursor=&limit=20&action="
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Upgrade-Insecure-Requests": "1",
    }

    response = requests.get(url, headers=headers, timeout=120)

    if response.status_code != 200:
        raise Exception("Request failed with status code: ", response.status_code)

    resp = response.json()

    _data = ResponseWithJSON.from_dict(resp)

    sort_datas = []

    datas = []

    if _data.data.items is not None:
        for item in _data.data.items:
            if item.resource is not None:
                if item.resource.uri is not None and item.resource.content_short is not None and item.resource.title is not None and item.resource.display_time is not None:
                    wallStreetNew = WallStreetSort(item.resource.title, item.resource.content_short, item.resource.uri,
                                                   item.resource.display_time)
                    sort_datas.append(wallStreetNew)

    sorted_datas = sorted(sort_datas, key=lambda x: x.display_time)

    for sorted_data in sorted_datas:
        wallStreetNew = WallStreetNew()
        wallStreetNew.title = sorted_data.title
        wallStreetNew.content = sorted_data.content
        wallStreetNew.url = sorted_data.url
        datas.append(wallStreetNew)

    return datas


if __name__ == '__main__':
    data = get_wallstreet_news()
    print(data)
