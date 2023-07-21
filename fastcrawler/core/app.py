import asyncio

from fastcrawler.exceptions import NoCrawlerFoundError
from fastcrawler.schedule.adopter import RocketryApplication, RocketryController
from fastcrawler.schedule.contracts import TaskControllerProto

from .crawler import Crawler


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

    controller: TaskControllerProto | None = None

    def __init__(
        self,
        crawlers: list[Crawler] | Crawler,
        controller: TaskControllerProto | None = None,
    ):
        """Initilize FastCrawler with defined crawlers"""
        if isinstance(crawlers, Crawler):
            self.crawlers = [
                crawlers,
            ]
        else:
            self.crawlers = crawlers

        self.controller = controller or RocketryController(app=RocketryApplication())
        if not self.crawlers or len(self.crawlers) == 0:
            raise NoCrawlerFoundError

    @property
    def get_all_serves(self):
        return [
            self.controller.app.serve(),
        ]

    async def serve(self) -> list[callable]:
        await asyncio.gather(*self.get_all_serves)

    async def run(self):
        for crawler in self.crawlers:
            await crawler.add_spiders()
        await self.serve()

    def run_sync(self):
        asyncio.run(self.run())

    async def startup(self):
        ...

    async def shutdown(self):
        ...

    async def _shutdown(self):
        await self.shutdown()
        for crawler in self.crawlers:
            await crawler.shut_down()
        await self.controller.shut_down()
