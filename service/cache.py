import datetime


class DailyCache:
    _instance = None

    def __init__(self):
        self.last_clear = datetime.datetime.now().date()
        self.cache = {}

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(DailyCache, cls).__new__(cls, *args, **kwargs)
            cls._instance.cache = {}
            cls._instance.last_clear = datetime.datetime.now().date()
        return cls._instance

    def get(self, key):
        if datetime.datetime.now().date() > self.last_clear:
            self.clear()
        return self.cache.get(key)

    def set(self, key, value):
        if datetime.datetime.now().date() > self.last_clear:
            self.clear()
        self.cache[key] = value

    def clear(self):
        self.cache.clear()
        self.last_clear = datetime.datetime.now().date()
