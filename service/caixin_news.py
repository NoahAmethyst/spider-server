import requests
from bs4 import BeautifulSoup

from pb import spider_pb2
from util.logger import logger


def get_caixin_news():
    domain_list = {
        'economy': '经济',
        'finance': '金融',
        'companies': '公司',
        'china': '政治',
        'international': '全球',
    }

    tag_list = {
        'tech': '科技',
        'property': '地产',
        'auto': '汽车',
        'energy': '能源',
        'livelihood': '民生',

    }

    domain_url = "https://{}.caixin.com/"
    base_url = "https://caixin.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 "
                      "Safari/537.36",
    }

    all_data = []

    for domain in domain_list.keys():
        url = domain_url.format(domain)
        response = requests.get(url, headers=headers, timeout=120)
        if response.status_code != 200:
            # raise Exception("Request failed with status code: ", response.status_code)
            logger.error(f'Request failed for domain【{domain}】with status code {response.status_code}')
            continue
        soup = BeautifulSoup(response.content, "html.parser")
        for selection in soup.select(".boxa"):
            parse_html(all_data, domain, domain_list, selection)
    # for tag in tag_list.keys():
    #     url = base_url + tag + '/'
    #     response = requests.get(url, headers=headers, timeout=120)
    #     if response.status_code != 200:
    #         raise Exception("Request failed with status code: ", response.status_code)
    #         logger.error(f'Request failed for tag【{tag}】with status code {response.status_code}')
    #         continue
    #     soup = BeautifulSoup(response.content, "html.parser")
    #     for selection in soup.select("dd"):
    #         parse_html(all_data, tag, tag_list, selection)
    news = []

    for i, data in enumerate(all_data):
        caixin_new = spider_pb2.CaiXinNew()
        caixin_new.url = data.get('url')
        caixin_new.title = data.get('title')
        caixin_new.description = data.get('desc')
        caixin_new.domain = data.get("domain")
        news.append(caixin_new)
    return news


def parse_html(all_data, domain, domain_list, selection):
    a = selection.find("a")
    _url = a.get("href")
    title = a.get_text()
    if title.__len__() == 0:
        title = selection.find('h4').getText()
    desc = selection.select_one("p").get_text()
    if _url:
        all_data.append({"title": title, "url": _url, "desc": desc, "domain": domain_list.get(domain)})
