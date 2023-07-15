from typing import Any, Type

from pydantic import ValidationError
from pydantic_core import Url

from fastcrawler.exceptions import ParserInvalidModelType, ParserValidationError
from fastcrawler.parsers.pydantic import BaseModel, BaseModelType, URLs


class JsonParser:
    """
    HTMLParser first initiate the scraped data, then it parses a given HTML document
        based on the specified model. Using Pydantic model with XPATHField or CSSField.
        Notice that this behavior is to seperate the process of saving in memory (Memory Bound)
        and process/clean the data (CPU Bound)


    Sample Usage:
        # first initiate the scraped data
        html_parser = HTMLParser(html)

        # parse it later!
        html_parser.parse(a pydantic model built with XPATHField or CSSField)
    """

    data = None

    def __init__(self, scraped_data: dict):
        """
        Initiate the JSON file in memory, so it can be parsed later
        as in MULTI PROCESS or etc.
        """
        self.scraped_data = scraped_data
        self.resolver: URLs | None = None

    def parse(self, model: Type[BaseModelType]) -> BaseModelType:
        """
        Parse using the pydantic model
        """
        if hasattr(model, "__mro__") and BaseModel in model.__mro__:  # type: ignore
            self.data: BaseModelType | Any = {}

            for field_name, field in model.model_fields.items():
                self.data[field_name] = self.scraped_data.get(field_name) or field.default

            if hasattr(model.Config, "url_resolver") and isinstance(model.Config.url_resolver, str):
                current_address: dict = self.scraped_data.copy()
                for address in model.Config.url_resolver.split("."):
                    current_address = current_address.get(address)  # type: ignore
                self.resolver = URLs(
                    urls=[
                        Url(current_address),
                    ]
                )
            try:
                self.data = model.model_validate(self.data)
            except ValidationError as error:
                raise ParserValidationError(error.errors()) from error
            return self.data
        else:
            raise ParserInvalidModelType(model=model)
