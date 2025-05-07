import os

import requests
from pb import spider_pb2


def get_zhihu_hot():
    url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=100"
    cookies = {
        'z_c0': os.getenv('ZHIHU_AUTH')
    }
    response = requests.get(url=url, cookies=cookies)

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")

    resp_data = response.json()

    hot_list = []
    for index, data in enumerate(resp_data['data']):
        zhihu_hot = spider_pb2.ZhihuHot()
        zhihu_hot.url = data['target']['url'].replace("api.", "").replace("questions", "question")
        zhihu_hot.title = data['target']['title']
        zhihu_hot.rank = index + 1
        zhihu_hot.excerpt = data['target']['excerpt']
        zhihu_hot.created = data['target']['created']
        hot_list.append(zhihu_hot)
    return hot_list
