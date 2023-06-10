from typing import TYPE_CHECKING, List, TypeVar, Union

from pydantic import AnyUrl
from pydantic import BaseModel as _BaseModel

if TYPE_CHECKING:
    from fastcrawler.parsers.selectors.base import \
        BaseSelector  # pragma: no cover


class BaseModel(_BaseModel):
    """
    Custom basemodel created from Pydantic :)
    """
    class Config:
        url_resolver: Union["BaseSelector", str]


class URLs(BaseModel):
    urls: List[AnyUrl | None] | None = []


T = TypeVar('T', bound=BaseModel)
