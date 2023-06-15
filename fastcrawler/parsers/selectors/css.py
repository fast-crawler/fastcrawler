# pylint: disable=c-extension-no-member

from typing import Any, Callable, List

from lxml import etree  # type: ignore[attr-defined]
from lxml import html as lxml_html  # type: ignore[attr-defined]

from fastcrawler.parsers.html import HTMLParser
from fastcrawler.parsers.pydantic import BaseModelType

from .base import BaseSelector


class _CSSField(BaseSelector):
    """
    CSSSelectorField represents a field that can be retrieved from a given HTML
        document using CSS selectors.
    """
    def __init__(
        self,
        query: str,
        extract: str | None = None,
        many: bool = False,
        model: Callable[..., BaseModelType] | None = None
    ):
        super(_CSSField, self).__init__(query, extract, many, model)
        self.parser = HTMLParser

    def resolve(
        self, scraped_data: str, model: None | BaseModelType = None
    ) -> BaseModelType | List[BaseModelType | Any] | None:
        """ Resolves HTML input using CSS selector
        """
        self.model = model or self.model
        tree = lxml_html.fromstring(scraped_data)
        results: List[etree.ElementBase] = tree.cssselect(self.query)
        res = self._process_results(results)
        return res


def CSSField(
    query: str,
    extract: str | None = None,
    many: bool = False,
    model: Callable[..., BaseModelType] | None = None
) -> Any:
    return _CSSField(query, extract, many, model)
