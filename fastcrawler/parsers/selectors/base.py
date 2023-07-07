# pylint: disable=c-extension-no-member

from typing import Any, Callable, List

from fastcrawler.parsers.base import ParserProtocol
from fastcrawler.parsers.pydantic import BaseModelType

from ..processors.base import ElementInterface, ProcessorInterface
from ..processors.lxml import LxmlProcessor


class BaseSelector:
    """Base class for HTML-based selectors that are dependent on lxml family.
    """

    parser: Callable[..., ParserProtocol]
    default_selector: ProcessorInterface = LxmlProcessor

    def __init__(
        self,
        query: str,
        extract: str | None = None,
        many: bool = False,
        model: Callable[..., BaseModelType] | None = None
    ):
        self.query = query
        self.extract = extract
        self.many = many
        self.model = model

    def __repr__(self):
        """Represents a selector for debugging purposes
        """
        return (
            f"Field(type={self.__class__.__name__} extract={self.extract}, "
            f"many={self.many}, query={self.query})"
        )

    def resolve(self, scraped_data, model):
        """Must be implemented by outer classes.
        Resolves the selector spefinalized by 'XPATH' or 'CSS' or etc
        """
        raise NotImplementedError(
            "Resolves must be overwritten by subclass"
            f"scraped_data={scraped_data}, model={model}"
        )

    def _process_results(
        self, results: List[ElementInterface]
    ) -> BaseModelType | List[BaseModelType | Any] | None:
        """Process the results resolved based on the logic
        which is combination of many, and extract.
        """
        if not results:
            return None

        elif self.many:
            results = [
                (self.get_from_exctract(result)) for result in results
            ]
            if self.model:
                results = [
                    self.parser(self.default_selector.to_string(el)).parse(self.model)
                    for el in results
                ]
            return results

        else:
            results = self.get_from_exctract(results[0])
            return results

    def get_from_exctract(self, result: ElementInterface) -> Any:
        """
        Resolve the extract from string, to get text from etree.ElementBase
            or to get other attributes or the string of HTML by default
        """
        if self.extract == "text":
            return result.text
        elif self.extract:
            return result.get(key=self.extract, default=None)
        elif not self.many and isinstance(result, self.default_selector.base_element):
            return self.default_selector.to_string(result)
        return result
