from typing import Any, Protocol


class ParserProtocol(Protocol):
    def __init__(self, data: Any): ...
    """Initilize the parser with the given data (html/json/etc)"""
    def parse(self, model: Any) -> Any: ...
    """
    Parse the saved data, with given model, which should be a pydantic model
        imported from fastcrawler library
    """
