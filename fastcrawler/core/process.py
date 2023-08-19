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
        """Initialize the crawler class

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
                name=f"{uuid4()}@{spider.__class__.__name__}",
            )
        self.args = args
        self.kwargs = kwargs
        self.spider: Spider = spider
        self.controller = controller

    async def start(self, silent: bool = True) -> None:
        """
        Start the crawling process explicitly.
        This method will disable scheduler temporarily to avoid duplicate running
        """
        if self.controller:
            await self.controller.toggle_task(str(self.task.name), new_status=False)
        await self.spider.start(silent=silent)
        if self.controller:
            await self.controller.toggle_task(str(self.task.name), new_status=True)
        return None

    async def stop(self) -> None:
        """Stop the crawling process"""
        for instance in self.spider.instances:
            instance.is_stopped = True

        if self.controller:
            await self.controller.toggle_task(str(self.task.name), new_status=False)
        return None

    async def add_spiders_to_controller(self) -> None:
        """
        Run the crawling process
        """
        assert self.controller is not None
        if self.task:
            await self.controller.add_task(self.spider.start, self.task)
        else:
            # TODO: raise custom error
            raise Exception("No condition found")
        return None
