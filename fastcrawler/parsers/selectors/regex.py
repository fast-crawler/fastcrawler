# pylint: disable=c-extension-no-member
import re
from typing import Any, Callable, List, Literal

from fastcrawler.parsers.html import HTMLParser
from fastcrawler.parsers.pydantic import BaseModelType
from fastcrawler.parsers.utils import _UNSET

from .base import BaseSelector


class _RegexField(BaseSelector):
    """
    RegexField represents a field that can be retrieved from a given HTML
    document using Regex.
    """

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        regex: Literal[""],
        default: Any = _UNSET,
        many: bool = False,
        model: Callable[..., BaseModelType] | None = None,
    ):
        self.parser = HTMLParser
        self.default = default
        self.regex = re.compile(regex)
        self.many = many
        self.model = model

    def resolve(
        self, scraped_data: str, model: BaseModelType | None = None
    ) -> BaseModelType | List[BaseModelType | Any] | None | Any:
        """Resolves HTML input as the Regex value given to list"""
        self.model = model or self.model
        if self.many:
            return re.findall(self.regex, scraped_data)
        else:
            result = re.search(self.regex, scraped_data)
            return result.group(1) if result else None


# pylint: disable=invalid-name
def RegexField(
    regex: Literal[r""],
    many: bool = False,
    model: Callable[..., BaseModelType] | None = None,
    default: Any = _UNSET,
) -> Any:
    """The reason that an object was initiated from class, and the class wasn't called directly
    is that because class __init__ method is returning only the instance of that class,
    and that's not what we want, we want to assign this to another type (ANY), so I should
    be using a function as interface to avoid IDE's error in type annotation or mypy.
    """
    return _RegexField(regex=regex, many=many, default=default, model=model)
