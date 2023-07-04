from typing import Callable, Protocol

from .schema import Task


class TaskApplicationProto(Protocol):
    task_lib: Callable

    def __init__(self, *args, **kwargs):
        """Initialize task application
        """

    async def serve(self, *args, **kwargs):
        """proto to serve with Uvicorn
        """

    async def get_all_tasks(self, *args, **kwargs) -> list[Task]: ...

    async def add_task(self, *args, **kwargs) -> None: ...

    async def start_up(self, *args, **kwargs) -> None: ...

    async def shut_down(self, *args, **kwargs) -> None: ...


class TaskControllerProto(Protocol):
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
