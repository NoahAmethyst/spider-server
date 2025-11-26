import os


class EnvConfig:
    _zhihu_auth = 'ZHIHU_AUTH'
    _juhe_api_key_exchange = 'JUHE_API_KEY_EXCHANGE'
    _juhe_api_key_gold = 'JUHE_API_KEY_GOLD'

    def __init__(self):
        pass

    @staticmethod
    def zhihu_auth() -> str:
        return os.getenv(EnvConfig._zhihu_auth)

    @staticmethod
    def juhe_exchange ():
        return os.getenv(EnvConfig._juhe_api_key_exchange)

    @staticmethod
    def juhe_gold ():
        return os.getenv(EnvConfig._juhe_api_key_gold)
