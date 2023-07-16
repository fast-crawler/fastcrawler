import datetime
from typing import Literal

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module
from rocketry.core import BaseCondition as _BaseCondition


class BaseCondition(_BaseCondition):  # pylint: disable=abstract-method
    """A condition is a thing/occurence that should happen in
    order to something happen.

    Conditions are used to determine whether a task can be started,
    a task should be terminated or the scheduler should shut
    down. Conditions are either true or false.

    A condition could answer for any of the following questions:
        - Current time is as specified (ie. Monday afternoon).
        - A given task has already run.
        - The machine has at least a given amount of RAM.
        - A specific file exists.

    Each condition should have the method ``__bool__`` specified
    as minimum. This method should return ``True`` or ``False``
    depending on whether the condition holds or does not hold.

    Examples
    --------

    Minimum example:

    >>> from rocketry.core import BaseCondition
    >>> class MyCondition(BaseCondition):
    ...     def __bool__(self):
    ...         ... # Code that defines state either
    ...         return True

    Complicated example with parser:

    >>> import os, re
    >>> class IsFooBar(BaseCondition):
    ...     __parsers__ = {
    ...         re.compile(r"is foo '(?P<outcome>.+)'"): "__init__"
    ...     }
    ...
    ...     def __init__(self, outcome):
    ...         self.outcome = outcome
    ...
    ...     def __bool__(self):
    ...         return self.outcome == "bar"
    ...
    ...     def __repr__(self):
    ...         return f"IsFooBar('{self.outcome}')"
    ...
    >>> from rocketry.parse import parse_condition
    >>> parse_condition("is foo 'bar'")
    IsFooBar('bar')
    """


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
        description="Logger name to be used in logging the task record", default=None
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
