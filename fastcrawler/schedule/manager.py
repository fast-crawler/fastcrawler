from typing import Callable, List

from rocketry import Rocketry
from rocketry.conditions.api import cron

from .schema import TaskSetting

# TODO: handle exception, raise error if task is not found
# TODO: Mock this taskmanager, then write tests for it :) DIP is included in __init__ as self.app


class TaskManager:
    def __init__(self, app: Rocketry):
        self.app = app

    @property
    def all(self) -> List[TaskSetting]:
        """
        Return all tasks from internal
        """

    def add_task(self, task_func: Callable, settings: TaskSetting) -> None:
        """
        Add tasks within internal python API
        """

    def change_task_scheldue(self, task_name: str, schedule: str) -> None:
        """
        Reschedule a task
            schedule:
                - can be string
                    `every 2 seconds`
                - can be cron
                    `*/2 * * * *`
        """
        for task in self.app.session.tasks:
            if task.name == task_name:
                if schedule.count(' ') == 4:
                    task.start_cond = cron(schedule)
                else:
                    task.start_cond = schedule
        return None

    def toggle_task(self, task_name: str) -> None:
        """
        Disables or enable one task
        """
        for task in self.app.session.tasks:
            if task.name == task_name:
                if task.disabled:
                    task.disabled = False
                else:
                    task.disabled = True
        return None
