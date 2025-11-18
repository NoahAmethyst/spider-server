from datetime import datetime

import requests

from pb import spider_pb2
from util.logger import logger


def get_odaily_feeds():
    feeds = []
    url = 'https://www.odaily.news/v1/openapi/feeds'
    headers = {
        'Cookie': 'acw_tc=dff7749f17044344276425489ecf256d29f8f1c4782dfbfdb20a7e3301',
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Request failed with status code: ", response.status_code)
    resp_data = response.json()

    for index, data in enumerate(resp_data['data']['arr_news']):
        odaily_feed = spider_pb2.OdailyFeed()
        odaily_feed.url = data['link']
        odaily_feed.title = data['title']
        odaily_feed.id = data['id']
        if data.get('description') is not None:
            odaily_feed.description = data['description']
        elif data.get('summary') is not None:
            odaily_feed.description = data['summary']
        if data.get('news_url') is not None:
            odaily_feed.reference_url = data['news_url']
        if data.get('published_at') is not None:
            date_format = "%Y-%m-%d %H:%M:%S"
            # Convert date string to datetime object
            dt = datetime.strptime(data['published_at'], date_format)
            # Convert datetime object to timestamp
            timestamp = int(dt.timestamp())
            odaily_feed.published_at = timestamp

        feeds.append(odaily_feed)
    return feeds
