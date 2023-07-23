import asyncio
from typing import Callable

from fastcrawler.exceptions import NoCrawlerFoundError
from fastcrawler.schedule.adopter import ProcessController, RocketryApplication
from fastcrawler.schedule.contracts import ControllerProto

from .process import Process


class FastCrawler:
    """The client interface to start all crawlers.
    Initialize all crawlers


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
        """Initialize FastCrawler with defined crawlers"""
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
    def get_all_serves(self) -> list[Callable]:
        """get all application to be served"""
        return [
            self.controller.app.serve(),
        ]

    async def serve(self) -> None:
        """Serve protocol for uvicorn"""
        await asyncio.gather(*self.get_all_serves)
        return None

    async def start(self, silent=True) -> None:
        """Start all crawlers in background explicitly without schedule"""
        await asyncio.gather(*[crawler.start(silent) for crawler in self.crawlers])
        return None

    async def run(self) -> None:
        """Run all crawlers in background explicitly with schedule"""
        for crawler in self.crawlers:
            await crawler.add_spiders()
        await self.serve()
        return None

    async def startup(self) -> None:
        """Start up event for application crawler"""
        return None

    async def shutdown(self) -> None:
        """Shut down event for application crawler"""
        return None

    async def _shutdown(self) -> None:
        """Safe shut down event for application crawler"""
        await self.shutdown()
        await self.controller.shut_down()
        return None
