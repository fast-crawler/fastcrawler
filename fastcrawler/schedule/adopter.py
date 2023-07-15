from typing import Callable

from rocketry import Rocketry
from rocketry.conditions.api import cron

from fastcrawler.exceptions import TaskNotFound

from .schema import Task


class RocketryApplication:
    def __init__(self, *args, **kwargs):
        self.task_lib: Rocketry = Rocketry(*args, **kwargs)

    async def serve(self, *args, **kwargs):  # pragma: no cover
        """Proto to serve with uvicorn"""
        await self.start_up()
        return await self.task_lib.serve(*args, **kwargs)

    async def get_all_tasks(self) -> set[Task]:
        return self.task_lib.session.tasks

    async def add_task(self, task_func: Callable, settings: Task) -> None:
        """
        ...
        """
        self.task_lib.task(**dict(settings))(task_func)
        return None

    async def start_up(self) -> None:
        """
        Run Startup Event
        """

    async def shut_down(self) -> None:
        self.task_lib.session.shut_down()
        return None


class RocketryController:
    def __init__(self, app: RocketryApplication):
        self.app = app

    async def all(self) -> set[Task]:
        """
        Return all tasks from internal
        """
        return await self.app.get_all_tasks()

    async def add_task(self, task_func: Callable, settings: Task) -> None:
        """
        Add tasks within internal python API
        """
        await self.app.add_task(task_func, settings)
        return None

    async def change_task_schedule(
        self,
        task_name: str,
        schedule: str,
    ) -> None:
        """
        Reschedule a task
            schedule:
                - can be string
                    `every 2 seconds`
                - can be cron
                    `*/2 * * * *`
        """
        for task in await self.app.get_all_tasks():
            if task.name == task_name:
                if schedule.count(" ") == 4:
                    task.start_cond = cron(schedule)
                else:
                    task.start_cond = schedule
                return None
        raise TaskNotFound(task_name)

    async def toggle_task(self, task_name: str) -> None:
        """
        Disables or enable one task
        """
        for task in await self.app.get_all_tasks():
            if task.name == task_name:
                if task.disabled:
                    task.disabled = False
                else:
                    task.disabled = True
                return None
        raise TaskNotFound(task_name)
