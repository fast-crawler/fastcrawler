class BaseModelError(Exception):
    """Base class for exceptions in this module."""


class NoCrawlerFoundError(BaseModelError):
    """No crawler is found in starting application"""

    def __init__(self):
        super().__init__(self, self.__doc__)


class ParserValidationError(BaseModelError):
    """Exception raised for errors in the input model validation from ParserValidationError."""


class ParserInvalidModelType(BaseModelError):
    """Exception raised for invalid type of the input model."""

    def __init__(self, model):
        self.model = model
        self.message = (
            f"The provided model {model} does not inherit from BaseModel."
            "Please provide a valid model that inherits from BaseModel"
            "\nfrom fastcrawler import BaseModel"
        )
        super().__init__(self.message)


class TaskNotFound(BaseModelError):
    def __init__(self, task_name):
        super().__init__(
            f"The Task with name={task_name} has not been found",
            "\nPlease check your input and be sure the task name is correct",
        )


class BadTaskException(BaseModelError):
    def __init__(self, task_name):
        super().__init__(
            f"The Task with name={task_name} has not been found",
            "\nPlease check your input and be sure the task name is correct",
        )


class NoCrawlerFound(BaseModelError):
    def __init__(self):
        super().__init__(
            "No task has been registered in the application."
            "\nPlease make sure that you've assigned the crawlers to the application"
            "so the application is aware of the crawlers."
            "\nThis may also raise if you have overridden the library's startup built in method"
        )


class ProcessorNotSupported(BaseModelError):
    def __init__(self, model):
        self.model = model
        self.message = (
            f"The provided processor {model} is not supported.\n"
            "To support the process, please explicitly map the processor"
            "inside the XPATH/CSS/Base selector, as a method called 'interface_mapper'"
            "\nWe support full duck typing which means you can inject whatever"
            "you need."
        )
        super().__init__(self.message)
