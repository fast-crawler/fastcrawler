from typing import List
from fastcrawler.core.spider import Spider


class CrawlerMeta(type):
    """
    Initiate the instances from base declarative

    DONT TOUCH THIS CLASS UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls._instances = {}


class Crawler(metaclass=CrawlerMeta):
    """
    Crawler class that implement the crawling process in background
    using the engine
    """

    def __new__(cls, *args, **kwargs):
        """
        Initiate the instances from base declarative
        Also saving args and kwargs so it can be used elsewhere

        DONT TOUCH THIS CLASS UNLESS YOU KNOW WHAT YOU ARE DOING.
        """
        instance = super().__new__(cls)
        cls._instances[instance] = args, kwargs
        return instance

    def __init__(self, task: List[Spider], *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.task = task

    @classmethod
    def get_all_objects(cls):
        """
        returns all instances inherited from this class
        """
        return cls._instances
