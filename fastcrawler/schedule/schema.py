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
    execution: Literal["main", "async", "thread", "process"] | None = None
    priority: int = 0
    disabled: bool = False
    force_run: bool = False
    status: Literal[
        "run", "fail", "success", "terminate", "inaction", "crash"
    ] | None = Field(description="Latest status of the task", default=None)
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
        arbitrary_types_allowed=True
        protected_namespaces = ()
