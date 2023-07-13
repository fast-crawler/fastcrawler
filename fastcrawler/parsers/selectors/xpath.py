# pylint: disable=c-extension-no-member

from typing import Any, Callable, List

from fastcrawler.parsers.html import HTMLParser
from fastcrawler.parsers.pydantic import BaseModelType
from fastcrawler.parsers.utils import _UNSET

from .base import BaseSelector


class _XPATHField(BaseSelector):
    """
    XPATHField represents a field that can be retrieved from a given HTML
    document using XPath.
    """

    def __init__(
        self,
        query: str,
        extract: str | None = None,
        many: bool = False,
        model: Callable[..., BaseModelType] | None = None,
        default: Any = _UNSET,
    ):
        super(_XPATHField, self).__init__(query, extract, many, model)
        self.parser = HTMLParser
        self.default = default

    def resolve(
        self, scraped_data: str, model: BaseModelType | None = None
    ) -> BaseModelType | List[BaseModelType | Any] | None:
        """Resolves HTML input as the xpath value given to list"""
        self.model = model or self.model
        results = self.processor.from_string_by_xpath(scraped_data, self.query)
        if not results:
            return self.default
        return self._process_results(results)


def XPATHField(
    query: str,
    extract: str | None = None,
    many: bool = False,
    model: Callable[..., BaseModelType] | None = None,
    default: Any = _UNSET,
) -> Any:
    """The reason that an object was initiated from class, and the class wasn't called directly
    is that because class __init__ method is returning only the instance of that class,
    and that's not what we want, we want to assign this to another type (ANY), so I should
    be using a function as interface to avoid IDE's error in type annotation or mypy.
    """
    return _XPATHField(query, extract, many, model, default)
