from typing import Any, get_args

from .pydantic import BaseModelType


def get_inner_model(model: list[BaseModelType] | Any, field_name: str) -> Any | BaseModelType:
    """Returns innter model in annotation type"""
    inner_model = get_args(model.__annotations__[field_name])
    return inner_model[0] if len(inner_model) > 0 else None


class UNSET:
    def __bool__(self):
        return False


_UNSET = UNSET()

__all__ = [
    "_UNSET",
    "get_inner_model",
]
