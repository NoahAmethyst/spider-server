import os


class EnvConfig:
    _zhihu_auth = 'ZHIHU_AUTH'
    _juhe_api_key_exchange = 'JUHE_API_KEY_EXCHANGE'
    _juhe_api_key_gold = 'JUHE_API_KEY_GOLD'
    _qqbot_grpc_addr = 'QQ_BOT_GRPC_ADDR'
    _weibo_alert_state_path = 'WEIBO_ALERT_STATE_PATH'

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

    @staticmethod
    def qqbot_grpc_addr() -> str:
        return os.getenv(EnvConfig._qqbot_grpc_addr)

    @staticmethod
    def weibo_alert_state_path() -> str:
        return os.getenv(EnvConfig._weibo_alert_state_path)
