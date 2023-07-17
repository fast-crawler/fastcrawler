from typing import List

from fastcrawler.exceptions import NoCrawlerFoundError

from .registery import Crawler


class FastCrawler:
    """The client interface to start all crawlers.
    Initilize all crawlers


    Usage:
        from your_module.spiders import wiki_spider
        app = FastCrawler(
            crawlers=wiki_spider
        )
        app.start()

    """

    crawlers: List[Crawler]

    def __init__(self, crawlers: List[Crawler] | Crawler):
        """Initilize FastCrawler with defined crawlers"""
        if isinstance(crawlers, Crawler):
            self.crawlers = [
                crawlers,
            ]
        else:
            self.crawlers = crawlers

        if not self.crawlers or len(self.crawlers) == 0:
            raise NoCrawlerFoundError
        # print(self.crawlers[0].task.instances)  # each spider
        # print(Crawler.get_all_objects())  # all crawlers args and etc

    async def serve(self):
        ...
