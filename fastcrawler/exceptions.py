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


class ProcessorNotSupported(BaseModelError):
    def __init__(self, model):
        self.model = model
        self.message = (
            f"The provided processor {model} is not supported.\n"
            "To support the process, please explictly map the processor"
            "inside the XPATH/CSS/Base selector, as a method called 'interface_mapper'"
            "\nWe support full duck typing which means you can inject whatever"
            "you need."
        )
        super().__init__(self.message)
