import datetime
from typing import Literal

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from .utilties import BaseCondition


class Task(BaseModel):
    name: str | None = Field(description="Name of the task. Must be unique")
    description: str | None = Field(
        description="Description of the task for documentation"
    )
    logger_name: str | None = Field(
        description="Logger name to be used in logging the task record"
    )
    execution: Literal["main", "async", "thread", "process"] | None
    priority: int = 0
    disabled: bool = False
    force_run: bool = False
    status: Literal[
        "run", "fail", "success", "terminate", "inaction", "crash"
    ] | None = Field(description="Latest status of the task")
    timeout: datetime.timedelta | None
    start_cond: BaseCondition
    end_cond: BaseCondition

    _last_run: float | None
    _last_success: float | None
    _last_fail: float | None
    _last_terminate: float | None
    _last_inaction: float | None
    _last_crash: float | None
