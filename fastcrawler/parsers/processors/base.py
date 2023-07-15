from typing import Protocol


class ElementInterface(Protocol):
    def get(self, key: str, default=None):
        """
        get method, which resolves an HTML element from a given key
            for instance:

            <a href=...>
            get(href) -> returns the href text inside the given element
                can also have default if nothing is found. Should be None.
        """

    @property
    def text(self):
        """
        Gets the inner text from an HTML element

            for instance:
                <li>Hello Mani :)</li>
                element.text -> 'Hello Mani'
        """


class ProcessorInterface(Protocol):
    base_element: ElementInterface = ...

    @staticmethod
    def to_string(result: ElementInterface) -> str:
        """
        Resolves a result to string, by getting the inner html,
        This method is used to iterate over HTML elements to resolve inner pydantic models
        """

    @staticmethod
    def from_string_by_xpath(
        string: str,
        query: str,
    ) -> list[ElementInterface] | ElementInterface | None:
        """
        Resolves a HTML string by XPATH
        """

    @staticmethod
    def from_string_by_css(
        string: str,
        query: str,
    ) -> list[ElementInterface] | ElementInterface | None:
        """
        Resolves a HTML string by CSS
        """
