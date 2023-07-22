# pragma: no cover
import logging
from typing import Mapping, Type, TypeVar

import coloredlogs
from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo
from redbird.templates import TemplateRepo

from fastcrawler.logger.schema import LogRecord

ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0
CRITICAL = 50

Repo = TypeVar("Repo", bound=TemplateRepo)
BaseRepoHandler = TypeVar("BaseRepoHandler", bound=RepoHandler)


class Logger:
    """
    Colored logger class that uses redbird logging and the Python logging module.

    Attributes:
        _logger (logging.Logger): The underlying logger instance from the logging module.
        formatter (str): The log message format. Default format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
        repo (Repo): The redbird repository to store log records.
        repo_handler (RepoHandler): The redbird repository handler to manage log records.

    Examples:
        Creating a basic logger:

        ```python
        >>> logger = Logger()
        >>> logger.info("This is an info message.")
        >>> logger.error("This is an error message.")
        ```

        Adding a custom handler to the logger:

        ```python
        >>> import logging

        >>> # Define a custom handler
        >>> custom_handler = logging.StreamHandler()
        >>> logger.add_handler(custom_handler)

        >>> logger.info("This message will be logged by the custom handler.")
        ```
    """

    _logger: logging.Logger = None
    formatter: str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )
    repo: Repo = None
    repo_handler: RepoHandler = None

    def __init__(
        self,
        name: str = "FastCrawler",
        level: int = NOTSET,
        redbird_repo: Type[Repo] = MemoryRepo,
        repo_handler: Type[BaseRepoHandler] = RepoHandler,
        formatter: str | None = None,
    ):
        """
        Initialize the logger.

        Args:
            name (str, optional): The logger name. Defaults to "FastCrawler".
            level (int, optional): The logging module log level. Defaults to NOTSET.
            redbird_repo (Type[Repo], optional): The redbird repository to store log records. Defaults to MemoryRepo.
            repo_handler (Type[BaseRepoHandler], optional): The redbird repository handler to manage log records.
                Defaults to RepoHandler.
            formatter (str | None, optional): The log message format. If None, the default format will be used.
                Defaults to None.
        """
        if formatter:
            self.formatter = formatter
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self.repo = redbird_repo(model=LogRecord)
        self.repo_handler = repo_handler(repo=self.repo, level=level)
        coloredlogs.install(
            level=level, logger=self._logger, use_colors=True, fmt=self.formatter, isatty=True
        )
        self._logger.addHandler(self.repo_handler)

    def log(
        self,
        msg: str,
        level: int,
        args=tuple[object, ...] | Mapping[str, object],
        stack_level: int = 3,
    ):
        """
        Log a message at the specified log level.

        Args:
            msg (str): The log message.
            level (int): The log level.
            args (tuple[object, ...] | Mapping[str, object], optional): Additional arguments to
                be passed to the log message. Defaults to an empty tuple.
            stack_level (int): logging module stack_level
        Note:
            The `stack_level` is set to 3 to trace the logging line number correctly.
        """
        self._logger._log(level=level, msg=msg, args=args, stacklevel=stack_level)

    def info(self, msg: str, *args) -> None:
        """
        Log an info-level message.

        Args:
            msg (str): The log message.
            *args: Additional arguments to be passed to the log message.
        """
        if self._logger.isEnabledFor(INFO):
            self.log(msg, INFO, args=args)

    def debug(self, msg: str, *args) -> None:
        """
        Log a debug-level message.

        Args:
            msg (str): The log message.
            *args: Additional arguments to be passed to the log message.
        """
        if self._logger.isEnabledFor(DEBUG):
            self.log(msg, DEBUG, args=args)

    def error(self, msg: str, *args) -> None:
        """
        Log an error-level message.

        Args:
            msg (str): The log message.
            *args: Additional arguments to be passed to the log message.
        """
        if self._logger.isEnabledFor(ERROR):
            self.log(msg, ERROR, args=args)

    def warning(self, msg: str, *args) -> None:
        """
        Log a warning-level message.

        Args:
            msg (str): The log message.
            *args: Additional arguments to be passed to the log message.
        """
        if self._logger.isEnabledFor(WARNING):
            self.log(msg, WARNING, args=args)

    def add_handler(self, handler: logging.Handler, formatter: str | None = None) -> None:
        """
        Add a custom handler to the logger.

        Args:
            handler (logging.Handler): The custom handler to be added.
            formatter (str | None, optional): The log message format for the custom handler.
              If None, the default format will be used. Defaults to None.
        """
        if formatter is None:
            formatter = self.formatter
        handler.formatter = logging.Formatter(formatter)

        self._logger.addHandler(handler)
