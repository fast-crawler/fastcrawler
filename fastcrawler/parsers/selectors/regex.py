import re
from typing import Any

from fastcrawler.parsers.html import HTMLParser
from fastcrawler.parsers.schema import BaseModelType
from fastcrawler.parsers.utils import _UNSET

from ..processors.contracts import ProcessorProcotol
from .base import BaseSelector


class _RegexField(BaseSelector):
    """
    RegexField represents a field that can be retrieved from a given HTML
    document using Regex.
    """

    def resolve(
        self, scraped_data: str, model: BaseModelType | list[BaseModelType | Any] | None = None
    ) -> BaseModelType | list[BaseModelType | Any] | None | Any:
        """Resolves HTML input as the Regex value given to list"""
        self.model = model or self.model
        if self.many:
            return re.findall(self.query, scraped_data)
        else:
            result = re.search(self.query, scraped_data)
            return result.group(1) if result else None


# pylint: disable=invalid-name
def RegexField(
    query: str,
    processor: None | ProcessorProcotol = None,
    parser=HTMLParser,
    many: bool = False,
    model: BaseModelType | list[BaseModelType | Any] | None = None,
    default: Any = _UNSET,
) -> Any:
    """The reason that an object was initiated from class, and the class wasn't called directly
    is that because class __init__ method is returning only the instance of that class,
    and that's not what we want, we want to assign this to another type (ANY), so I should
    be using a function as interface to avoid IDE's error in type annotation or mypy.
    """
    return _RegexField(
        query=query,
        many=many,
        model=model,
        default=default,
        parser=parser,
        processor=processor,
    )
