# pragma: no cover

from abc import ABC, abstractmethod, abstractstaticmethod
from typing import Callable

from .schema import Task


class ApplicationABC(ABC):  # pragma: no cover
    @abstractmethod
    def run(self) -> None:
        """Run the task application"""

    @abstractmethod
    async def serve(self, *args, **kwargs):
        """Proto to serve with Uvicorn"""

    @abstractmethod
    def get_all_session_tasks(self) -> set[Task]:
        """Returns all tasks that exists in application"""

    @abstractmethod
    async def get_all_tasks(self) -> list[Task]:
        """Returns all tasks that exists in application"""

    @abstractmethod
    async def add_task(self, *args, **kwargs) -> None:
        """Dynamically add a task to application"""

    @abstractmethod
    async def shut_down(self) -> None:
        """Execute shut down"""

    @abstractstaticmethod
    async def inject_string_condition_to_task(cond: str, task: Task) -> Task:  # type: ignore
        """Inject condition to a task. Like a cron or a string condition"""


class ControllerABC(ABC):  # pragma: no cover
    app: ApplicationABC

    @abstractmethod
    async def all(self) -> list[Task]:
        """
        Return all tasks from internal on controller level
        """

    @abstractmethod
    async def add_task(self, task_func: Callable, settings: Task) -> None:
        """
        Add tasks within internal python API
        On controller level
        """

    @abstractmethod
    async def change_task_schedule(self, task_name: str, schedule: str) -> None:
        """
        Reschedule a task
            schedule:
                - can be string
                    `every 2 seconds`
                - can be cron
                    `*/2 * * * *`
        """

    @abstractmethod
    async def toggle_task(self, task_name: str, new_status: bool) -> None:
        """
        Disables or enable one task
        """

    @abstractmethod
    async def start_up(self) -> None:
        """Manage start up on controller level"""

    @abstractmethod
    async def shut_down(self) -> None:
        """Manage shut down on controller level"""

    @abstractmethod
    async def serve(self) -> None:
        """Run the task application from controller level"""

    @abstractmethod
    def run(self):
        """Run the crawler processor without uvicorn"""
