# pylint: disable=c-extension-no-member

from typing import Any, Callable, List

from fastcrawler.parsers.html import HTMLParser
from fastcrawler.parsers.pydantic import BaseModelType
from lxml import etree  # type: ignore[attr-defined]
from lxml import html as lxml_html  # type: ignore[attr-defined]

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
        default: Any = None,
        use_default: bool = True
    ):
        super(_XPATHField, self).__init__(query, extract, many, model)
        self.parser = HTMLParser
        self.default = default
        self.use_default = use_default

    def resolve(
        self, scraped_data: str, model: BaseModelType | None = None
    ) -> BaseModelType | List[BaseModelType | Any] | None:
        """Resolves HTML input as the xpath value given to list
        """
        self.model = model or self.model
        tree = lxml_html.fromstring(scraped_data)
        results: List[etree.ElementBase] = tree.xpath(self.query)
        if not results and self.use_default:
            return self.default
        return self._process_results(results)


def XPATHField(
    query: str,
    extract: str | None = None,
    many: bool = False,
    model: Callable[..., BaseModelType] | None = None,
    default: Any = None,
    use_default: bool = True
) -> Any:
    return _XPATHField(query, extract, many, model, default, use_default)
