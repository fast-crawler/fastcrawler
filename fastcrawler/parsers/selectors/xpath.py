from typing import Any, List

from lxml import etree
from lxml import html as lxml_html

from fastcrawler.parsers.html import HTMLParser
from fastcrawler.parsers.pydantic import T

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
        model: T | None = None
    ):
        super(_XPATHField, self).__init__(query, extract, many, model)
        self.parser = HTMLParser

    def resolve(self, html: str, model: T | None = None) -> T | list[T | None]:
        """Resolves HTML input as the xpath value given to list
        """
        self.model = model or self.model
        tree = lxml_html.fromstring(html)
        results: List[etree.ElementBase] = tree.xpath(self.query)
        return self._process_results(results)


def XPATHField(**kwargs) -> Any:
    return _XPATHField(**kwargs)
