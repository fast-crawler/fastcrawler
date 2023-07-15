from typing import Type

from pydantic import ValidationError
from pydantic_core import Url

from fastcrawler.exceptions import ParserInvalidModelType, ParserValidationError

from .schema import BaseModel, BaseModelType, URLs
from .selectors.base import BaseSelector, get_selector
from .utils import get_inner_model


class HTMLParser:
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

    def __init__(self, scraped_data: str):
        """
        Initiate the HTML file in memory, so it can be parsed later
        as in MULTI PROCESS or etc.
        """
        self.scraped_data = scraped_data
        self.resolver: URLs | None = None
        self.data = None

    def parse(self, model: Type[BaseModelType]) -> BaseModelType:
        """
        Parse using the pydantic model
        """
        if issubclass(model, BaseModel):  # type: ignore
            data = {}
            for field_name, field in model.model_fields.items():
                fastcrawler_selector = get_selector(field)
                if fastcrawler_selector:
                    data[field_name] = fastcrawler_selector.resolve(
                        scraped_data=self.scraped_data,
                        model=get_inner_model(
                            model, field_name
                        ),  # TODO: check if pydantic returns the model data type
                    )

            if hasattr(
                model.Config,
                "url_resolver",
            ) and issubclass(model.Config.url_resolver.__class__, BaseSelector):
                urls: list[Url] = model.Config.url_resolver.resolve(  # type: ignore
                    self.scraped_data,
                    model=None,
                )
                self.resolver = URLs(urls=urls or [])

            try:
                self.data: BaseModelType | None = model.model_validate(data)
                return self.data
            except ValidationError as error:
                raise ParserValidationError(error.errors()) from error

        else:
            raise ParserInvalidModelType(model=model)
