# pylint: skip-file


from fastcrawler import BaseModel, CSSField, RegexField, XPATHField

# from fastcrawler.parsers import ModestProcessor


class ListItem(BaseModel):
    id: int | None = XPATHField(query="//a/@id")
    name: str | None = XPATHField(query="//a", extract="text")
    source: str = "https://mywebsite.com"
    source_as_default: None | str = XPATHField(
        query="//a[@nothing]",
        extract="text",
        default="Nothing",
    )


class TestModel(BaseModel):
    items: list[ListItem] = XPATHField(query="//ul/li", many=True)


class VeryNested(BaseModel):
    items: list[TestModel] = XPATHField(query="//table", many=True)

    class Config:
        url_resolver = XPATHField(
            query="//ul[@class='pagination']//a",
            extract="href",
            many=True,
        )


class InnerHTML(BaseModel):
    table: str | None = XPATHField(query="//table", default=None)


class ListItemCSS(BaseModel):
    id: int | None = CSSField(query="a", extract="id")
    name: str | None = CSSField(query="a", extract="text")
    source_as_default: None | str = CSSField(
        query="nav",
        extract="text",
        default="Nothing",
    )


class TestModelCSS(BaseModel):
    items: list[ListItemCSS] = CSSField(query="li", many=True)


class VeryNestedCSS(BaseModel):
    items: list[TestModelCSS] = CSSField(query="table", many=True)

    class Config:
        url_resolver = CSSField(
            query="ul.pagination > li > a",
            many=True,
            extract="href",
        )


class ListItemJson(BaseModel):
    id: int | None
    name: str | None


class VeryNestedJson(BaseModel):
    results: list[ListItemJson]

    class Config:
        url_resolver = "pagination.next_page"


class LinksData(BaseModel):
    link: list = RegexField(regex=r"href=['\"]([^'\"]+)['\"]", many=True)


class LinksDataSingle(BaseModel):
    link: str = RegexField(regex=r"href=['\"]([^'\"]+)['\"]")


class EmailData(BaseModel):
    emails: list | None = RegexField(regex=r"[\w.-]+@[\w.-]+\.\w+", default=None)


# class MDT_Item(BaseModel):
#     id: int | None = CSSField(processor=ModestProcessor, query="a", extract="id")
#     name: str | None = CSSField(processor=ModestProcessor, query="a", extract="text")
#     source_as_default: None | str = CSSField(
#         processor=ModestProcessor,
#         query="nav",
#         extract="text",
#         default="Nothing",
#     )


# class MDT_ItemList(BaseModel):
#     items: list[ListItemCSS] = CSSField(
#         processor=ModestProcessor,
#         query="li",
#         many=True,
#     )


# class MDT_NestedItemList(BaseModel):
#     items: list[TestModelCSS] = CSSField(
#         processor=ModestProcessor,
#         query="table",
#         many=True,
#     )

#     class Config:
#         url_resolver = CSSField(
#             processor=ModestProcessor,
#             query="ul.pagination > li > a",
#             many=True,
#             extract="href",
#         )


# class MDT_FlatList(BaseModel):
#     link: str = CSSField(
#         processor=ModestProcessor,
#         query="ul > li > a",
#     )


class RandomElement:
    ...


class RandomProcessor:
    def from_string_by_xpath(self, something):
        return [RandomElement()]


class NotSupportedProcessor(BaseModel):
    id: str = XPATHField(
        processor=RandomProcessor,
        query="(//table//li//a)[1]",
        default=None,
        extract="href",
    )
