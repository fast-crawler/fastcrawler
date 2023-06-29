# pylint: disable=c-extension-no-member
import re
from typing import Any, Callable, List, Literal

from fastcrawler.parsers.html import HTMLParser
from fastcrawler.parsers.pydantic import BaseModelType

from .base import BaseSelector


class _RegexField(BaseSelector):
    """
    RegexField represents a field that can be retrieved from a given HTML
    document using Regex.
    """
    def __init__(
        self,
        regex: Literal[''],
        default: Any = None,
        many: bool = False,
        model: Callable[..., BaseModelType] | None = None,
        has_default: bool = True
    ):
        self.parser = HTMLParser
        self.default = default
        self.regex = regex
        self.many = many
        self.model = model
        self.has_default = has_default

    def resolve(
        self, scraped_data: str, model: BaseModelType | None = None
    ) -> BaseModelType | List[BaseModelType | Any] | None | Any:
        """Resolves HTML input as the Regex value given to list
        """
        self.model = model or self.model
        if self.many:
            return re.findall(self.regex, scraped_data)
        else:
            result = re.search(self.regex, scraped_data)
            return result.group(1) if result else None


def RegexField(
    regex: Literal[r""],
    many: bool = False,
    model: Callable[..., BaseModelType] | None = None,
    default: Any = None,
    has_default: bool = True
) -> Any:
    return _RegexField(
        regex=regex, many=many, default=default, model=model, has_default=has_default
    )
