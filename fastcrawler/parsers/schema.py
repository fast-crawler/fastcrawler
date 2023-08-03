from typing import TYPE_CHECKING, Literal, TypeVar, Union

from pydantic import AnyUrl
from pydantic import BaseModel as _BaseModel

if TYPE_CHECKING:
    from fastcrawler.parsers.selectors.base import BaseSelector  # pragma: no cover


class MappedAttr(_BaseModel):
    is_property: bool
    attr_name: str


class MappedResult(_BaseModel):
    get: MappedAttr
    text: MappedAttr


class BaseModel(_BaseModel):
    """
    Custom basemodel created from Pydantic :)
    """

    class Config:
        url_resolver: Union["BaseSelector", str]
        http_method: Literal["get", "post", "delete", "put"] = "get"
        next_resolver: Union["BaseSelector", str]


class URLs(BaseModel):
    urls: list[AnyUrl] = []


BaseModelType = TypeVar("BaseModelType", bound=BaseModel)
