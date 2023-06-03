from typing import Optional, List
from fastcrawler import BaseModel, XPATHField, XPathList
from fastcrawler.parsers import HTMLParser, JsonParser


class ListItem(BaseModel):
    id: Optional[int] = XPATHField(xpath="//a/@id")
    name: str = XPATHField(xpath="//a/text()")


class TestModel(BaseModel):
    items: List[ListItem] = XPathList(xpath="//ul/li")


class VeryNested(BaseModel):
    items: List[TestModel] = XPathList(xpath="//table")

    class Config:
        url_resolver = XPATHField(xpath="//ul[@class='pagination']//a/@href")


class ListItemJson(BaseModel):
    id: Optional[int]
    name: str


class VeryNestedJson(BaseModel):
    results: List[ListItemJson]

    class Config:
        url_resolver = "pagination.next_page"


html_parser = HTMLParser("""
<html>
    <body>
        <table>
            <ul>
                <li><a href='http://address.com/seller/ali' id='100'>Link 1</a></li>
                <li><a href='http://address.com/seller/gholi' id='200'>Link 2</a></li>
                <li><a href='http://address.com/seller/abbas' id='300'>Link 3</a></li>
            </ul>
        </table>
        <nav>
            <ul class="pagination">
                <li><a href="http://address.com/item?page=1" class="active">1</a></li>
                <li><a href="http://address.com/item?page=2">2</a></li>
                <li><a href="http://address.com/item?page=3">3</a></li>
            </ul>
        </nav>
    </body>
</html>
""")

parser = html_parser.parse(VeryNested)
assert parser.items[0].items[0].id == 100
assert parser.items[0].items[0].name == "Link 1"
assert len(parser.items[0].items) == 3
assert len(html_parser.resolver.urls) == 3
assert str(html_parser.resolver.urls[2]) == "http://address.com/item?page=3"


_json = {
        "results": [
            {
                "id": 1,
                "name": "Link 1"
            },
            {
                "id": 2,
                "name": "Link 2"
            },
            {
                "id": 3,
                "name": "Link 3"
            }
        ],
        "pagination": {
            "next_page": "http://address.com/item?page=3",
            "last_page": "http://address.com/item?page=1"
        },
        "end_page": "http://address.com/item?page=100"
    }

json_parser = JsonParser(
    _json
)


_json_parse_results = json_parser.parse(VeryNestedJson)
assert len(_json_parse_results.results) == len(_json["results"])
assert _json_parse_results.results[0].id == _json["results"][0]["id"]
assert _json_parse_results.results[2].name == _json["results"][2]["name"]
assert len(json_parser.resolver.urls) == 1
assert str(json_parser.resolver.urls[0]) == _json["pagination"]["next_page"]
