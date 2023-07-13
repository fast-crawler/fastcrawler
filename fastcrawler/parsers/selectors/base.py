# pylint: disable=c-extension-no-member

from typing import Any, Callable, List

from pydantic.fields import FieldInfo

from fastcrawler.exceptions import ProcessorNotSupported
from fastcrawler.parsers.base import ParserProtocol
from fastcrawler.parsers.pydantic import BaseModelType, MappedAttr, MappedResult

from ..processors.base import ElementInterface, ProcessorInterface
from ..processors.lxml import LxmlProcessor


class BaseSelector:
    """Base class for HTML-based selectors that are dependent on lxml family."""

    parser: Callable[..., ParserProtocol]

    def __init__(
        self,
        query: str,
        extract: str | None = None,
        many: bool = False,
        model: Callable[..., BaseModelType] | None = None,
        processor: ProcessorInterface = LxmlProcessor,
    ):
        self.query = query
        self.extract = extract
        self.many = many
        self.model = model
        self.processor = processor

    def __repr__(self):
        """Represents a selector for debugging purposes"""
        return (
            f"Field(type={self.__class__.__name__} extract={self.extract}, "
            f"many={self.many}, query={self.query})"
        )

    def resolve(self, scraped_data, model):
        """Must be implemented by outer classes.
        Resolves the selector spefinalized by 'XPATH' or 'CSS' or etc
        """
        raise NotImplementedError(
            "Resolves must be overwritten by subclass" f"scraped_data={scraped_data}, model={model}"
        )

    def _process_results(
        self,
        results: List[ElementInterface],
    ) -> BaseModelType | List[BaseModelType | Any] | None:
        """Process the results resolved based on the logic
        which is combination of many, and extract.
        """
        if not results:
            return None

        elif self.many:
            results = [(self.get_from_exctract(result)) for result in results]
            if self.model:
                results = [
                    self.parser(self.processor.to_string(el)).parse(self.model) for el in results
                ]
            return results

        results = self.get_from_exctract(results[0])
        return results

    def interface_mapper(self, cls: object) -> MappedResult:
        """Translate interface hardcoded to adopt to different C external library

        Understand that all libraries mapped here are actually written with C,
            so it was not possible at this time to monkey patch them.

        Best solution to force same interface with them is to design
            a mapper that does it explictly, this may be deprecated later
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
            raise ProcessorNotSupported(cls.__class__)

    def call_from_mapper(self, result, mapped: MappedAttr, *args, **kwargs):
        return (
            getattr(result, mapped.attr_name)(*args, **kwargs)
            if not mapped.is_property
            else getattr(result, mapped.attr_name)
        )

    def get_from_exctract(self, result: ElementInterface) -> Any:
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
            and issubclass(type(result), self.processor.base_element.__mro__[1])
        ):
            # Return: HTML string of object result
            return self.processor.to_string(result)
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
