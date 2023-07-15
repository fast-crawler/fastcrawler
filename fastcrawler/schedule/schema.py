import datetime
from typing import Literal

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from .utilties import BaseCondition


class Task(BaseModel):
    """Base class for Tasks.

    A task can be a function, command or other procedure that
    does a specific thing. A task can be parametrized by supplying


    Parameters
    ----------
    name : str, optional
        Name of the task. Ideally, all tasks
        should have unique name. If None, the
        return value of Task.get_default_name()
        is used instead.
    description : str, optional
        Description of the task. This is purely
        for task documentation purpose.
    start_cond : BaseCondition, optional
        Condition that when True the task
        is to be started, by default AlwaysFalse()
    end_cond : BaseCondition, optional
        Condition that when True the task
        will be terminated. Only works for for
        tasks with execution='process' or 'thread'
        if thread termination is implemented in
        the task, by default AlwaysFalse()
    execution : str, {'main', 'thread', 'process'}, default='process'
        How the task is executed. Allowed values
        'main' (run on main thread & process),
        'thread' (run on another thread) and
        'process' (run on another process).
    disabled : bool
        If True, the task is not allowed to be run
        regardless of the start_cond,
        by default False
    force_run : bool
        If True, the task will be run once
        regardless of the start_cond,
        by default True
    priority : int, optional
        Priority of the task. Higher priority
        tasks are first inspected whether they
        can be executed. Can be any numeric value.
        Setup tasks are recommended to have priority
        >= 40 if they require loaded tasks,
        >= 50 if they require loaded extensions.
        By default 0
    timeout : str, int, timedelta, optional
        If the task has not run in given timeout
        the task will be terminated. Only applicable
        for tasks with execution='process' or
        with execution='thread'.

    Examples
    --------
    Minimum example:

    >>> from fastcrawler.schedule.schema import Task
    >>> class MyTask(Task):
    ...     def execute(self):
    ...         ... # What the task does.
    ...         return ...

    """

    name: str | None = Field(description="Name of the task. Must be unique")
    description: str | None = Field(description="Description of the task for documentation")
    logger_name: str | None = Field(
        description="Logger name to be used in logging the task record"
    )
    execution: Literal["main", "async", "thread", "process"] | None = None
    priority: int = 0
    disabled: bool = False
    force_run: bool = False
    status: Literal["run", "fail", "success", "terminate", "inaction", "crash"] | None = Field(
        description="Latest status of the task", default=None
    )
    timeout: datetime.timedelta | None = None
    start_cond: BaseCondition | None = None
    end_cond: BaseCondition | None = None

    _last_run: float | None = None
    _last_success: float | None = None
    _last_fail: float | None = None
    _last_terminate: float | None = None
    _last_inaction: float | None = None
    _last_crash: float | None = None

    class Config:
        arbitrary_types_allowed = True
        protected_namespaces = ()
        underscore_attrs_are_private = True
        validate_assignment = True
