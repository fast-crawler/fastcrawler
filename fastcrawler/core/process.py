from uuid import uuid4

from fastcrawler.core.spider import Spider
from fastcrawler.schedule.contracts import ControllerProto
from fastcrawler.schedule.schema import Task


class Process:
    """
    Crawler class that implement the crawling process in background
    using the engine
    """

    def __init__(
        self,
        spider: Spider,
        controller: ControllerProto | None = None,
        cond: str | Task | None = None,
        *args,
        **kwargs,
    ):
        """Initilize the crawler class

        Args:
            spider (Spider): _description_
            controller (None | ControllerProto, optional): _description_. Defaults to None.
            cond (Task | None, optional): _description_. Defaults to None.
        """
        if isinstance(cond, Task):
            self.task = cond
        else:
            self.task = Task(
                start_cond=cond or "every 1 second",
                name=spider.__class__.__name__ + str(uuid4()),
            )
        self.args = args
        self.kwargs = kwargs
        self.spider: Spider = spider
        self.controller = controller

    async def start(self, silent: bool = True):
        """
        Start the crawling process explictly.
        This method will disable scheduler temporarily to avoid duplicate running
        """
        if self.controller:
            await self.controller.toggle_task(self.task.name, new_status=False)
        await self.spider.start(silent=silent)
        if self.controller:
            await self.controller.toggle_task(self.task.name, new_status=True)

    async def stop(self):
        """Stop the crawling process"""
        self.spider.is_stopped = True
        if self.controller:
            self.controller.toggle_task(self.task.name, new_status=False)

    async def add_spiders(self):
        """
        Run the crawling process
        """
        if self.task:
            await self.controller.add_task(self.spider.start, self.task)
        else:
            # TODO: raise custom error
            raise Exception("No condition found")
