from typing import Type


from pydantic import ValidationError


from fastcrawler.parsers.pydantic import URLs, BaseModel, T
from fastcrawler.exceptions import ParserInvalidModelType, ParserValidationError


class JsonParser:
    """
    JsonParser parses a given JSON document based on the specified pydantic model.
    """
    def __init__(self, json: str):
        """
        Initiate the JSON file in memory, so it can be parsed later
        as in MULTI PROCESS or etc.
        """
        self.json: dict = json
        self.resolver: URLs = []

    def parse(self, model: Type[T]) -> T:
        """
        Parse using the pydantic model
        """
        if BaseModel in model.__mro__:
            data = {}
            for field_name, field in model.model_fields.items():
                data[field_name] = self.json.get(field_name) or field.default

            if hasattr(model.Config, "url_resolver"):
                current_address = self.json
                for address in model.Config.url_resolver.split("."):
                    current_address = current_address.get(address)
                self.resolver = URLs(urls=[current_address, ])
            try:
                self.data: T = model.model_validate(data)
            except ValidationError as error:
                raise ParserValidationError(error.errors())
            return self.data
        else:
            raise ParserInvalidModelType(model=model)
