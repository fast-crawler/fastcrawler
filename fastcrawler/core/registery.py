from typing import List
from fastcrawler.core.spider import Spider


class CrawlerMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls._instances = {}


class Crawler(metaclass=CrawlerMeta):
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        cls._instances[instance] = args, kwargs
        return instance

    def __init__(self, task: List[Spider], *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.task = task

    @classmethod
    def get_all_objects(cls):
        return cls._instances
