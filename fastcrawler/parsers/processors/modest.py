from selectolax.parser import HTMLParser, Node

from .base import ElementInterface


class ModestProcessor:
    base_element = Node

    @staticmethod
    def to_string(result: Node) -> str:
        """
        Resolves a result to string, by getting the inner html,
        This method is used to iterate over HTML elements to resolve inner pydantic models
        """
        return result.html

    @staticmethod
    def from_string_by_xpath(
        string: str, query: str
    ) -> list[ElementInterface] | ElementInterface | None:
        """
        Resolves a HTML string by XPATH
        """
        raise NotImplementedError("XPATH is not supported in selectolax")

    @staticmethod
    def from_string_by_css(
        string: str, query: str
    ) -> list[ElementInterface] | ElementInterface | None:
        """
        Resolves a HTML string by CSS
        """
        results = HTMLParser(string).css(query)
        return results
