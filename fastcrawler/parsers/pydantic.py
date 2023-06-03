from typing import Union, List, Optional, TypeVar, get_args, TYPE_CHECKING


from pydantic import (
    BaseModel as _BaseModel,
    AnyUrl
)


if TYPE_CHECKING:
    from fastcrawler.parsers.html import XPATHField  # pragma: no cover


class BaseModel(_BaseModel):
    class Config:
        url_resolver: Union["XPATHField", str]


class URLs(BaseModel):
    urls: Optional[List[Union[AnyUrl, None]]] = []


T = TypeVar('T', bound=BaseModel)


def get_inner_model(model: BaseModel, field_name: str):
    inner_model = get_args(
        model.__annotations__[field_name]
    )
    return inner_model[0] if len(inner_model) > 0 else None
