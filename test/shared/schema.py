# pylint: skip-file

from typing import List, Optional

from fastcrawler import BaseModel, CSSField, XPATHField


class ListItem(BaseModel):
    id: Optional[int] = XPATHField(query="//a/@id")
    name: str = XPATHField(query="//a", extract="text")
    source: str = "https://mywebsite.com"


class TestModel(BaseModel):
    items: List[ListItem] = XPATHField(query="//ul/li", many=True)


class VeryNested(BaseModel):
    items: List[TestModel] = XPATHField(query="//table", many=True)

    class Config:
        url_resolver = XPATHField(
            query="//ul[@class='pagination']//a",
            extract="href",
            many=True
        )


class InnerHTML(BaseModel):
    table: str | None = XPATHField(query="//table")


class ListItemCSS(BaseModel):
    id: Optional[int] = CSSField(query="a", extract="id")
    name: Optional[str] = CSSField(query="a", extract="text")


class TestModelCSS(BaseModel):
    items: List[ListItemCSS] = CSSField(query="li", many=True)


class VeryNestedCSS(BaseModel):
    items: List[TestModelCSS] = CSSField(query="table", many=True)

    class Config:
        url_resolver = CSSField(
            query="ul.pagination > li > a", many=True, extract="href"
        )


class ListItemJson(BaseModel):
    id: Optional[int]
    name: str


class VeryNestedJson(BaseModel):
    results: List[ListItemJson]

    class Config:
        url_resolver = "pagination.next_page"
