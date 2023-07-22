import asyncio

from fastcrawler.exceptions import NoCrawlerFoundError
from fastcrawler.schedule.adopter import ProcessController, RocketryApplication
from fastcrawler.schedule.contracts import ControllerProto

from .process import Process


class FastCrawler:
    """The client interface to start all crawlers.
    Initilize all crawlers


    Usage:
        from your_module.spiders import wiki_spider
        app = FastCrawler(
            crawlers=wiki_spider
        )
        asyncio.run(app.run())

    """

    controller: ControllerProto | None = None

    def __init__(
        self,
        crawlers: list[Process] | Process,
        controller: ControllerProto | None = None,
    ):
        """Initilize FastCrawler with defined crawlers"""
        ...
        if isinstance(crawlers, Process):
            self.crawlers = [
                crawlers,
            ]
        else:
            self.crawlers = crawlers

        self.controller = controller or ProcessController(app=RocketryApplication())
        if not self.crawlers or len(self.crawlers) == 0:
            raise NoCrawlerFoundError

    @property
    def get_all_serves(self):
        """get all application to be served"""
        return [
            self.controller.app.serve(),
        ]

    async def serve(self) -> list[callable]:
        """Serve protocol for uvicorn"""
        await asyncio.gather(*self.get_all_serves)

    async def start(self, silent=True):
        """Start all crawlers in background explictly without schedule"""
        await asyncio.gather(*[crawler.start(silent) for crawler in self.crawlers])

    async def run(self):
        """Run all crawlers in background explictly with schedule"""
        for crawler in self.crawlers:
            await crawler.add_spiders()
        await self.serve()

    async def startup(self):
        """Start up event for application crawler"""

    async def shutdown(self):
        """Shut down event for application crawler"""

    async def _shutdown(self):
        """Safe shut down event for application crawler"""
        await self.shutdown()
        await self.controller.shut_down()
