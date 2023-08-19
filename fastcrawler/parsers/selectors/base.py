from typing import Any, Callable

from pydantic.fields import FieldInfo

from fastcrawler.exceptions import ProcessorNotSupportedError
from fastcrawler.parsers.contracts import ParserProtocol
from fastcrawler.parsers.schema import BaseModelType, MappedAttr, MappedResult
from fastcrawler.parsers.utils import _UNSET

from ..processors.contracts import ElementProtocol, ProcessorProtocol
from ..processors.lxml import LxmlProcessor


class BaseSelector:
    """Base class for HTML-based selectors that are dependent on lxml family."""

    def __init__(
        self,
        query: str,
        parser: Callable[..., ParserProtocol] | None = None,
        processor: ProcessorProtocol | None = None,
        extract: str | None = None,
        many: bool = False,
        model: BaseModelType | list[BaseModelType | Any] | None = None,
        default: Any = _UNSET,
    ):
        self.query = query
        self.extract = extract
        self.many = many
        self.model = model
        self.processor = processor or LxmlProcessor
        self.default = default
        self.parser = parser

    def __repr__(self):
        """Represents a selector for debugging purposes"""
        return (
            f"Field(type={self.__class__.__name__} extract={self.extract},"
            f" many={self.many}, query={self.query})"
        )

    def resolve(self, scraped_data, model):
        """Must be implemented by outer classes.
        Resolves the selector specialized by 'XPATH' or 'CSS' or etc
        """
        raise NotImplementedError(
            "Resolves must be overwritten by subclass"
            f"scraped_data={scraped_data}, model={model}"
        )

    def _process_results(
        self,
        results: list[ElementProtocol],
    ) -> BaseModelType | list[BaseModelType | Any] | list[ElementProtocol] | None:
        """Process the results resolved based on the logic
        which is combination of many, and extract.
        """

        if self.many:
            results = [(self.get_from_extract(result)) for result in results]
            if self.model:
                results = [
                    self.parser(self.processor.to_string(el)).parse(self.model)  # type: ignore
                    for el in results  # type: ignore
                ]
            return results

        results = self.get_from_extract(results[0])
        return results

    def interface_mapper(self, cls: object) -> MappedResult:
        """Translate interface hardcoded to adopt to different C external library

        Understand that all libraries mapped here are actually written with C,
            so it was not possible at this time to monkey patch them.

        Best solution to force same interface with them is to design
            a mapper that does it explicitly, this may be deprecated later
            if the library maintainer help us by allowing us to monkey patch
            as we need
        """
        if "lxml" in cls.__module__:
            return MappedResult(
                get=MappedAttr(is_property=False, attr_name="get"),
                text=MappedAttr(is_property=True, attr_name="text"),
            )
        elif "selectolax" in cls.__module__:
            return MappedResult(
                get=MappedAttr(is_property=False, attr_name="css"),
                text=MappedAttr(is_property=False, attr_name="text"),
            )
        else:
            raise ProcessorNotSupportedError(cls.__class__)

    def call_from_mapper(self, result, mapped: MappedAttr, *args, **kwargs):
        return (
            getattr(result, mapped.attr_name)(*args, **kwargs)
            if not mapped.is_property
            else getattr(result, mapped.attr_name)
        )

    def get_from_extract(self, result: ElementProtocol) -> Any:
        """
        Resolve the extract from string, to get text from etree.ElementBase
            or to get other attributes or the string of HTML by default
            based on the logic of representation

        This is a dirty implementation because we could not monkey patch or change
            the design of external C-Extension libraries
        """
        if self.extract == "text":
            # Return: inner text
            return self.call_from_mapper(result, self.interface_mapper(result).text)
        elif self.extract:
            # Return: attr from html
            return self.call_from_mapper(
                result,
                self.interface_mapper(result).get,
                self.extract,
            )
        elif (
            not self.extract
            and not self.many
            and issubclass(type(result), self.processor.base_element)  # type: ignore
        ):
            # Return: HTML string of object result
            return self.processor.to_string(result)  # type: ignore
        else:  # Return: inner HTML element objects to parse nested models
            return result


def get_selector(field: FieldInfo) -> BaseSelector | None:
    """
    Checks for subclass of "BaseSelector", and returns if it has.

    This function was mainly written for type annotation on the source code.
    """
    if issubclass(field.default.__class__, BaseSelector):
        return field.default
    return None
