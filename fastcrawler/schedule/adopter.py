from functools import partial
from typing import Callable

from rocketry import Rocketry  # type: ignore
from rocketry.conditions.api import cron  # type: ignore
from rocketry.core.task import Task as RocketryTask

from fastcrawler.exceptions import BadTaskException, TaskNotFound

from .contracts import ApplicationABC, ControllerProto
from .schema import Task


def callable_to_partial(method: Callable) -> partial | None:
    if hasattr(method, "__self__"):
        if method.__self__ is not None:
            return partial(method)
        instance = method.__self__.__class__()
        return partial(method, instance)
    return None


class RocketryApplication(ApplicationABC):
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

    async def get_all_tasks(self) -> list[Task]:
        """Returns a copy of all tasks that exists in application"""
        return list(Task(**task.dict()) for task in self.task_lib.session.tasks)

    def get_all_session_tasks(self) -> set[RocketryTask]:
        """Returns all tasks that exists in application"""
        return self.task_lib.session.tasks

    async def add_task(self, task_func: Callable, settings: Task) -> None:
        """Dynamically add a task to application"""
        task_as_callable = callable_to_partial(task_func)
        if task_as_callable is None:
            raise BadTaskException(task_func)
        self.task_lib.task(**settings.model_dump(exclude_unset=True))(task_as_callable)
        return None

    async def shut_down(self) -> None:
        """Execute shut down"""
        self.task_lib.session.shut_down()
        return None

    @staticmethod
    async def inject_string_condition_to_task(cond: str, task: Task) -> Task:
        """Inject condition to a task. Like a cron or a string condition"""
        if cond.count(" ") == 4:
            task.start_cond = cron(cond)
        else:
            task.start_cond = cond
        return task


class ProcessController(ControllerProto):
    def __init__(self, app: ApplicationABC):
        """Initialize task application

        Args:
            app (TaskProcessor): _description_
        """
        self.app = app

    async def all(self) -> list[Task]:
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
        for task in self.app.get_all_session_tasks():
            if task.name == task_name:
                await self.app.inject_string_condition_to_task(cond=schedule, task=task)
                return None
        raise TaskNotFound(task_name)

    async def toggle_task(self, task_name: str, new_status=None) -> None:
        """
        Disables or enable one task
        """
        for task in self.app.get_all_session_tasks():
            if task.name == task_name:
                if new_status is None:
                    task.disabled = not task.disabled
                else:
                    task.disabled = not new_status
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
