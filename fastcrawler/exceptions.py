class BaseModelError(Exception):
    """Base class for exceptions in this module."""


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
