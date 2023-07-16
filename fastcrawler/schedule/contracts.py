# pragma: no cover

from typing import Callable, Protocol

from .schema import Task


class TaskApplicationProto(Protocol):  # pragma: no cover
    task_lib: Callable

    def __init__(self, *args, **kwargs):
        """Initialize task application"""

    async def serve(self, *args, **kwargs):
        """Proto to serve with Uvicorn"""

    async def get_all_tasks(self) -> set[Task]:
        """Returns all tasks that exists in Fast Crawler"""

    async def add_task(self, *args, **kwargs) -> None:
        """Dynamically add a task to fast crawler"""

    async def start_up(self) -> None:
        """Manage start up actvity"""

    async def shut_down(self) -> None:
        """Manage shut down activity"""


class TaskControllerProto(Protocol):  # pragma: no cover
    app: TaskApplicationProto

    def __init__(self, app: TaskApplicationProto):
        """Initialize task application

        Args:
            app (TaskProcessor): _description_
        """

    async def all(self) -> list[Task]:
        """
        Return all tasks from internal
        """

    async def add_task(self, task_func: Callable, settings: Task) -> None:
        """
        Add tasks within internal python API
        """

    async def change_task_schedule(self, task_name: str, schedule: str) -> None:
        """
        Reschedule a task
            schedule:
                - can be string
                    `every 2 seconds`
                - can be cron
                    `*/2 * * * *`
        """

    async def toggle_task(self, task_name: str) -> None:
        """
        Disables or enable one task
        """
