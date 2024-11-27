import os

from binance import Client


class BinanceCli:
    _instance = None

    def __init__(self):
        self.client = Client(os.environ.get('BINANCE_API_KEY'), os.environ.get('BINANCE_API_SECRET'))

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(BinanceCli, cls).__new__(cls, *args, **kwargs)
            cls._instance.client = Client(os.environ.get('BINANCE_API_KEY'), os.environ.get('BINANCE_API_SECRET'))
        return cls._instance

