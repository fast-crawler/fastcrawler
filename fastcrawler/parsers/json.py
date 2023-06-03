from typing import Type


from fastcrawler.parsers.pydantic import URLs, BaseModel, T


class JsonParser:
    """
    JsonParser parses a given JSON document based on the specified model.
    """
    def __init__(self, json: str):
        self.json: dict = json
        self.resolver: URLs = []

    def parse(self, model: Type[T]) -> T:
        if BaseModel in model.__mro__:
            data = {}
            for field_name, field in model.model_fields.items():
                data[field_name] = self.json.get(field_name) or field.default

            if hasattr(model.Config, "url_resolver"):
                current_address = self.json
                for address in model.Config.url_resolver.split("."):
                    current_address = current_address.get(address)
                self.resolver = URLs(urls=[current_address, ])
            self.data: T = model.model_validate(data)
            return self.data
