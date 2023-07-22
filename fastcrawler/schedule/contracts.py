# pragma: no cover

from typing import Callable, Protocol

from .schema import Task


class ApplicationProto(Protocol):  # pragma: no cover
    task_lib: Callable

    def __init__(self, *args, **kwargs):
        """Initialize task application"""

    def run(self) -> None:
        """Run the task application"""

    async def serve(self, *args, **kwargs):
        """Proto to serve with Uvicorn"""

    async def get_all_tasks(self) -> set[Task]:
        """Returns all tasks that exists in application"""

    async def add_task(self, *args, **kwargs) -> None:
        """Dynamically add a task to application"""

    async def shut_down(self) -> None:
        """Execute shut down"""

    async def inject_string_condition_to_task(self, cond: str, task: Task) -> Task:
        """Inject condition to a task. Like a cron or a string condition"""


class ControllerProto(Protocol):  # pragma: no cover
    app: ApplicationProto

    def __init__(self, app: ApplicationProto):
        """Initialize task application

        Args:
            app (TaskProcessor): _description_
        """

    async def all(self) -> set[Task]:
        """
        Return all tasks from internal on controller level
        """

    async def add_task(self, task_func: Callable, settings: Task) -> None:
        """
        Add tasks within internal python API
        On controller level
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

    async def start_up(self) -> None:
        """Manage start up on controller level"""

    async def shut_down(self) -> None:
        """Manage shut down on controller level"""

    async def serve(self) -> None:
        """Run the task application from controller level"""

    def run(self):
        """Run the crawler processor without uvicorn"""
