from pydantic import BaseModel


class ConfigDataClass:
    silence_task_prerun: bool
    silence_task_logging: bool
    silence_cond_check: bool


class TaskSetting(BaseModel):
    ...
