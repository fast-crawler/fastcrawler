from typing import get_args

from pydantic.main import FieldInfo

from fastcrawler.parsers.selectors.base import BaseSelector

from .pydantic import BaseModel


def get_inner_model(model: BaseModel, field_name: str):
    """ Returns innter model in annotation type
    """
    inner_model = get_args(
        model.__annotations__[field_name]
    )
    return inner_model[0] if len(inner_model) > 0 else None


def get_selector(field: FieldInfo) -> BaseSelector | None:
    """
    Checks for subclass of BaseSelector, and returns if it has.

    This function was mainly written for type annotation on the source code.
    """
    if issubclass(field.default.__class__, BaseSelector):
        return field.default
    return None
