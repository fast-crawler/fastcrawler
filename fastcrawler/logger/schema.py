from pydantic import BaseModel, Field


class LogRecord(BaseModel):
    """A logging record

    See attributes: https://docs.python.org/3/library/logging.html#logrecord-attributes
    """

    name: str
    msg: str
    levelname: str
    levelno: int
    pathname: str
    filename: str
    module: str
    exc_info: str | None
    exc_text: str | None
    stack_info: str | None
    lineno: int
    funcName: str
    created: float
    msecs: float
    relativeCreated: float
    thread: int
    threadName: str
    processName: str
    process: int
    message: str

    formatted_message: str = Field(
        description="Formatted message. This field is created by RepoHandler."
    )
