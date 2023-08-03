# pragma: no cover
# pylint: disable=c-extension-no-member
from typing import Any, Callable, Protocol

from fastcrawler.parsers.contracts import ParserProtocol
from fastcrawler.parsers.schema import BaseModelType
from fastcrawler.parsers.utils import _UNSET

from ..processors.contracts import ProcessorProtocol


class SelectorProto(Protocol):
    """Base class for HTML-based selectors that are dependent on lxml family."""

    def __init__(
        self,
        query: str,
        parser: Callable[..., ParserProtocol] | None = None,
        processor: ProcessorProtocol | None = None,
        extract: str | None = None,
        many: bool = False,
        model: Callable[..., BaseModelType] | None = None,
        default: Any = _UNSET,
    ):
        """Initiate selector"""

    def __repr__(self):
        """Represents a selector for debugging purposes"""

    def resolve(self, scraped_data, model):
        """Must be implemented by outer classes.
        Resolves the selector specialized by 'XPATH' or 'CSS' or etc
        """
