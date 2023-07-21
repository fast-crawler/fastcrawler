from fastcrawler.core.spider import Spider
from fastcrawler.schedule.adopter import RocketryApplication, RocketryController
from fastcrawler.schedule.contracts import TaskControllerProto
from fastcrawler.schedule.schema import Task


class Crawler:
    """
    Crawler class that implement the crawling process in background
    using the engine
    """

    def __init__(
        self,
        spider: Spider,
        controller: None | TaskControllerProto = None,
        cond: Task | None = None,
        *args,
        **kwargs,
    ):
        self.task = Task(start_cond=cond or "every 1 second", name="something")
        self.args = args
        self.kwargs = kwargs
        self.spider: Spider = spider
        self.controller = controller or RocketryController(app=RocketryApplication())

    async def start(self):
        """
        Start the crawling process explictly
        """
        await self.start_up()
        for task in self.spider.instances:
            await task.start()

    async def add_spiders(self):
        """
        Run the crawling process
        """
        if self.task:
            await self.controller.add_task(self.spider.start, self.task)
        else:
            # TODO: raise custom error
            raise Exception("No condition found")

    def run(self):
        return self.controller.run()

    async def start_up(self):
        ...

    async def shut_down(self):
        ...

    async def _shutdown(self):
        await self.shut_down()
        for task in self.spider.instances:
            await task.shut_down()
