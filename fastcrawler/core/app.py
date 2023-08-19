import asyncio
from typing import Any, Coroutine

from fastcrawler.exceptions import NoCrawlerFoundErrorError
from fastcrawler.schedule.adopter import ProcessController, RocketryApplication
from fastcrawler.schedule.contracts import ControllerABC

from .process import Process


def list_process(crawlers: list[Process] | Process) -> list[Process]:
    if isinstance(crawlers, Process):
        return [crawlers]
    else:
        return crawlers


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

    controller: ControllerABC | None = None

    def __init__(
        self,
        crawlers: list[Process] | Process,
        controller: ControllerABC | None = None,
    ):
        """Initialize FastCrawler with defined crawlers"""
        self.crawlers = list_process(crawlers)
        self.controller = controller or ProcessController(app=RocketryApplication())
        if not self.crawlers or len(self.crawlers) == 0:
            raise NoCrawlerFoundErrorError

    @property
    def get_all_serves(self) -> list[Coroutine[Any, Any, None]]:
        """get all application to be served"""
        assert self.controller is not None
        return [
            self.controller.app.serve(),
        ]

    async def serve(self) -> None:
        """
        Serve protocol for uvicorn, useful with combination
            with other tools if get_all_serves is customized
        """
        await asyncio.gather(*self.get_all_serves)
        return None

    async def start(self, silent=True) -> None:
        """Start all crawlers in background explicitly without schedule"""

        # TODO: make here multi processing, for more than one process!
        # or use rocketry to trigger the tasks, if possible :)
        await asyncio.gather(*[crawler.start(silent) for crawler in self.crawlers])
        return None

    async def run(self) -> None:
        """Run all crawlers in background explicitly with schedule"""
        for crawler in self.crawlers:
            crawler.controller = self.controller
            await crawler.add_spiders_to_controller()
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
        assert self.controller is not None
        await self.shutdown()
        await self.controller.shut_down()
        return None
