from typing import Type

from pydantic import ValidationError

from fastcrawler.exceptions import (ParserInvalidModelType,
                                    ParserValidationError)

from .proto import ParserProtocol
from .pydantic import BaseModel, T, URLs
from .selectors.base import BaseSelector
from .utilities import get_inner_model, get_selector


class HTMLParser(ParserProtocol):
    """
    HTMLParser parses a given HTML document based on the specified model.
    Using Pydantic model with XpathFIELD and xpahtlist

    Sample Usage:
        html_parser = HTMLParser(html)
        html_parser.parse(a pydantic model)
    """

    def __init__(self, extract: str):
        """
        Initiate the HTML file in memory, so it can be parsed later
        as in MULTI PROCESS or etc.
        """
        self.extract = extract
        self.resolver: URLs | None = None
        self.data: T | None = None

    def parse(self, model: Type[T] | None = None) -> T:
        """
        Parse using the pydantic model
        """
        if hasattr(model, "__mro__") and BaseModel in model.__mro__:
            data = {}
            for field_name, field in model.model_fields.items():
                field_selector = get_selector(field)
                if field_selector:
                    data[field_name] = field_selector.resolve(
                        html=self.extract,
                        model=get_inner_model(model, field_name)
                    )

            if hasattr(
                model.Config, "url_resolver",
            ) and issubclass(model.Config.url_resolver.__class__, BaseSelector):
                self.resolver = URLs(
                    urls=model.Config.url_resolver.resolve(
                        self.extract
                    )
                )

            try:
                self.data: T = model.model_validate(data)
            except ValidationError as error:
                raise ParserValidationError(error.errors())

            return self.data

        else:
            raise ParserInvalidModelType(model=model)
