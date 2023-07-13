# pylint: skip-file

from typing import List, Optional

from fastcrawler import BaseModel, CSSField, RegexField, XPATHField


class ListItem(BaseModel):
    id: Optional[int] = XPATHField(query="//a/@id")
    name: str = XPATHField(query="//a", extract="text")
    source: str = "https://mywebsite.com"
    source_as_default: None | str = XPATHField(
        query="//a[@nothing]", extract="text", default="Nothing"
    )


class TestModel(BaseModel):
    items: List[ListItem] = XPATHField(query="//ul/li", many=True)


class VeryNested(BaseModel):
    items: List[TestModel] = XPATHField(query="//table", many=True)

    class Config:
        url_resolver = XPATHField(
            query="//ul[@class='pagination']//a",
            extract="href",
            many=True,
        )


class InnerHTML(BaseModel):
    table: str | None = XPATHField(query="//table", default=None)


class ListItemCSS(BaseModel):
    id: Optional[int] = CSSField(query="a", extract="id")
    name: Optional[str] = CSSField(query="a", extract="text")
    source_as_default: None | str = CSSField(
        query="nav",
        extract="text",
        default="Nothing",
    )


class TestModelCSS(BaseModel):
    items: List[ListItemCSS] = CSSField(query="li", many=True)


class VeryNestedCSS(BaseModel):
    items: List[TestModelCSS] = CSSField(query="table", many=True)

    class Config:
        url_resolver = CSSField(
            query="ul.pagination > li > a",
            many=True,
            extract="href",
        )


class ListItemJson(BaseModel):
    id: Optional[int]
    name: str


class VeryNestedJson(BaseModel):
    results: List[ListItemJson]

    class Config:
        url_resolver = "pagination.next_page"


class LinksData(BaseModel):
    link: list = RegexField(regex=r"href=['\"]([^'\"]+)['\"]", many=True)


class LinksDataSingle(BaseModel):
    link: str = RegexField(regex=r"href=['\"]([^'\"]+)['\"]")


class EmailData(BaseModel):
    emails: list | None = RegexField(regex=r"[\w.-]+@[\w.-]+\.\w+", default=None)
