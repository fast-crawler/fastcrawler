from typing import Protocol


class ElementInterface(Protocol):
    def get(self, key, default=None): ...

    @property
    def text(self): ...


class ProcessorInterface(Protocol):
    base_element: ElementInterface = ...

    @staticmethod
    def to_string(result: ElementInterface): ...

    @staticmethod
    def from_string_by_xpath(string: str, query: str) -> ElementInterface: ...

    @staticmethod
    def from_string_by_css(string: str, query: str) -> ElementInterface: ...
