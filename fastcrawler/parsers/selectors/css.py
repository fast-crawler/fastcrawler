from typing import Any, List

from lxml import etree
from lxml import html as lxml_html

from fastcrawler.parsers.html import HTMLParser
from fastcrawler.parsers.pydantic import T

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
        model: T | None = None
    ):
        super(_CSSField, self).__init__(query, extract, many, model)
        self.parser = HTMLParser

    def resolve(self, html: str, model: None | T = None) -> T | list[T | None]:
        """ Resolves HTML input using CSS selector
        """
        self.model = model or self.model
        tree = lxml_html.fromstring(html)
        results: List[etree.ElementBase] = tree.cssselect(self.query)
        res = self._process_results(results)
        return res


def CSSField(**kwargs) -> Any:
    return _CSSField(**kwargs)
