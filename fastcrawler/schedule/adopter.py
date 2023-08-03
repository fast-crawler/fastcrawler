from functools import partial
from typing import Callable

from rocketry import Rocketry  # type: ignore
from rocketry.conditions.api import cron  # type: ignore

from fastcrawler.exceptions import TaskNotFound

from .contracts import ApplicationProto
from .schema import Task


def make_callable(method: Callable | type):
    if hasattr(method, "__self__"):
        if method.__self__ is not None:
            return partial(method)
        else:
            instance = method.__self__.__class__()
            return partial(method, instance)
    else:
        return method


class RocketryApplication:
    def __init__(self, *args, **kwargs):
        """Initialize A Rocketry Application to process crawlers"""
        self.task_lib: Rocketry = Rocketry(*args, **kwargs)

    def run(self, *args, **kwargs) -> None:
        self.task_lib.run(*args, **kwargs)
        return None

    async def serve(self, *args, **kwargs) -> None:
        """Proto to serve with Uvicorn"""
        await self.task_lib.serve(*args, **kwargs)
        return None

    async def get_all_tasks(self) -> set[Task]:
        """Returns all tasks that exists in application"""
        return self.task_lib.session.tasks

    async def add_task(self, task_func: Callable, settings: Task) -> None:
        """Dynamically add a task to application"""
        task_func = make_callable(task_func)
        self.task_lib.task(**settings.model_dump(exclude_unset=True))(task_func)
        return None

    async def shut_down(self) -> None:
        """Execute shut down"""
        self.task_lib.session.shut_down()
        return None

    async def inject_string_condition_to_task(self, cond: str, task: Task) -> Task:
        """Inject condition to a task. Like a cron or a string condition"""
        if cond.count(" ") == 4:
            task.start_cond = cron(cond)
        else:
            task.start_cond = cond
        return task


class ProcessController:
    def __init__(self, app: ApplicationProto):
        """Initialize task application

        Args:
            app (TaskProcessor): _description_
        """
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
                self.app.inject_string_condition_to_task(cond=schedule, task=task)
                return None
        raise TaskNotFound(task_name)

    async def toggle_task(self, task_name: str, new_status=None) -> None:
        """
        Disables or enable one task
        """
        for task in await self.app.get_all_tasks():
            if task.name == task_name:
                if new_status is None:
                    if task.disabled:
                        task.disabled = False
                    else:
                        task.disabled = True
                else:
                    task.disabled = new_status
                return None
        raise TaskNotFound(task_name)

    async def start_up(self) -> None:
        """
        Run Startup Event
        """
        return None

    async def shut_down(self) -> None:
        """Shut down controller for crawler processor"""
        await self.app.shut_down()
        return None

    async def serve(self, *args, **kwargs):  # pragma: no cover
        """Proto to serve with uvicorn"""
        await self.start_up()
        await self.app.serve(*args, **kwargs)
        return None

    def run(self):
        """Run the crawler processor without uvicorn"""
        return self.app.run()
