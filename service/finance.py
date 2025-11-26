import requests

from pb import spider_pb2
from pb.spider_pb2 import FinanceResp
from util.config import EnvConfig
from util.logger import logger


class FinanceJuheApi:
    def __init__(self):
        self.api_key_exchange = EnvConfig.juhe_exchange()
        self.api_key_gold = EnvConfig.juhe_gold()
        self.currency_map = {
            "人民币": "CNY",
            "美金": "USD",
            "美元": "USD",
            "日元": "JPY",
            "欧元": "EUR",
            "英镑": "GBP",
            "韩元": "KER",
            "港币": "HKD",
            "越南盾": "VND",
            "卢布": "RUB",
            "澳大利亚元": "AUD",
            "澳元": "AUD",
            "加拿大元": "CAD",
            "加币": "CAD",
            "新加坡元": "SGD",
            "新台币": "TWD",
            "泰国铢": "THB",
            "阿尔及利亚第纳尔": "DZD",
            "阿根廷比索": "ARS",
            "爱尔兰镑": "IEP",
            "埃及镑": "EGP",
            "阿联酋迪拉姆": "AED",
            "阿曼里亚尔": "OMR",
            "奥地利先令": "ATS",
            "澳门元": "MOP",
            "百慕大元": "BMD",
            "巴基斯坦卢比": "PKR",
            "巴拉圭瓜拉尼": "PYG",
            "巴林第纳尔": "BHD",
            "巴拿马巴尔博亚": "PAB",
            "保加利亚列弗": "BGN",
            "巴西雷亚尔": "BRL",
            "比利时法郎": "BEF",
            "冰岛克朗": "ISK",
            "博茨瓦纳普拉": "BWP",
            "波兰兹罗提": "PLN",
            "玻利维亚诺": "BOB",
            "丹麦克朗": "DKK",
            "德国马克": "DEM",
            "法国法郎": "FRF",
            "菲律宾比索": "PHP",
            "芬兰马克": "FIM",
            "哥伦比亚比索": "COP",
            "古巴比索": "CUP",
            "哈萨克坚戈": "KZT",
            "荷兰盾": "NLG",
            "加纳塞地": "GHC",
            "捷克克朗": "CZK",
            "津巴布韦元": "ZWD",
            "卡塔尔里亚尔": "QAR",
            "克罗地亚库纳": "HRK",
            "肯尼亚先令": "KES",
            "科威特第纳尔": "KWD",
            "老挝基普": "LAK",
            "拉脱维亚拉图": "LVL",
            "黎巴嫩镑": "LBP",
            "林吉特": "MYR",
            "立陶宛立特": "LTL",
            "罗马尼亚新列伊": "RON",
            "毛里求斯卢比": "MUR",
            "蒙古图格里克": "MNT",
            "孟加拉塔卡": "BDT",
            "缅甸缅元": "BUK",
            "秘鲁新索尔": "PEN",
            "摩洛哥迪拉姆": "MAD",
            "墨西哥比索": "MXN",
            "南非兰特": "ZAR",
            "挪威克朗": "NOK",
            "葡萄牙埃斯库多": "PTE",
            "瑞典克朗": "SEK",
            "瑞士法郎": "CHF",
            "沙特里亚尔": "SAR",
            "斯里兰卡卢比": "LKR",
            "索马里先令": "SOS",
            "坦桑尼亚先令": "TZS",
            "土耳其新里拉": "TRY",
            "突尼斯第纳尔": "TND",
            "危地马拉格查尔": "GTQ",
            "委内瑞拉玻利瓦尔": "VEB",
            "乌拉圭新比索": "UYU",
            "西班牙比塞塔": "ESP",
            "希腊德拉克马": "GRD",
            "新西兰元": "NZD",
            "匈牙利福林": "HUF",
            "牙买加元": "JMD",
            "义大利里拉": "ITL",
            "印度卢比": "INR",
            "印尼盾": "IDR",
            "以色列谢克尔": "ILS",
            "约旦第纳尔": "JOD",
            "智利比索": "CLP"
        }

    def currency_list(self) -> FinanceResp:
        resp = spider_pb2.FinanceResp()
        resp.str_list.extend(list(self.currency_map.keys()))
        return resp

    def exchange_rate(self, _from: str, _to: str) -> FinanceResp:
        resp = spider_pb2.FinanceResp()
        requestParams = {
            'key': self.api_key_exchange,
            'from': _from,
            'to': _to,
            'version': '2',
        }
        response = requests.get(url='http://op.juhe.cn/onebox/exchange/currency', params=requestParams)
        # 检查请求是否成功
        result_list = response.json().get("result", [])

        if not result_list:
            logger.error('exchange rate list is none')
            return resp

        # 提取第一条汇率信息（通常是最相关的）
        first_result = result_list[0]
        resp.float_value = float(first_result.get("result"))
        return resp

    def gold_price(self) -> FinanceResp:
        resp = spider_pb2.FinanceResp()
        requestParams = {
            'key': self.api_key_gold,
            'v': '1',
        }
        response = requests.get(url='http://web.juhe.cn/finance/gold/shgold', params=requestParams)

        result_list = response.json().get("result", [])

        if not result_list:
            logger.error('gold price is none')
            return resp

        # 提取第一条汇率信息（通常是最相关的）
        first_result = result_list[0]
        last_price = first_result.get("latestpri")
        resp.float_value = float(last_price)
        return resp


def test_exchange_rate():
    result = FinanceJuheApi().exchange_rate('USD', "CNY")
    print(result)


def test_gold_price():
    FinanceJuheApi().gold_price()
