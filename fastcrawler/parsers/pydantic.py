from typing import List, TypeVar, get_args, TYPE_CHECKING, Union


from pydantic import (
    BaseModel as _BaseModel,
    AnyUrl
)


if TYPE_CHECKING:
    from fastcrawler.parsers.html import XPATHField  # pragma: no cover


class BaseModel(_BaseModel):
    """
    Custom basemodel created from Pydantic :)
    """
    class Config:
        url_resolver: Union["XPATHField", str]


class URLs(BaseModel):
    urls: List[AnyUrl | None] | None = []


T = TypeVar('T', bound=BaseModel)


def get_inner_model(model: BaseModel, field_name: str):
    """ Returns innter model in annotation type
    """
    inner_model = get_args(
        model.__annotations__[field_name]
    )
    return inner_model[0] if len(inner_model) > 0 else None
