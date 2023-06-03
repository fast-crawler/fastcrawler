import pytest
from typing import Optional, List
from fastcrawler import BaseModel, XPATHField, XPathList
from fastcrawler.exceptions import ParserValidationError, ParserInvalidModelType
from fastcrawler.parsers import HTMLParser, JsonParser


class ListItem(BaseModel):
    id: Optional[int] = XPATHField(xpath="//a/@id")
    name: str = XPATHField(xpath="//a", value="text")


class TestModel(BaseModel):
    items: List[ListItem] = XPathList(xpath="//ul/li")


class VeryNested(BaseModel):
    items: List[TestModel] = XPathList(xpath="//table")

    class Config:
        url_resolver = XPATHField(
            xpath="//ul[@class='pagination']//a", many=True, value="href"
        )


class ListItemJson(BaseModel):
    id: Optional[int]
    name: str


class VeryNestedJson(BaseModel):
    results: List[ListItemJson]

    class Config:
        url_resolver = "pagination.next_page"


@pytest.fixture
def html():
    return """
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
    """


@pytest.fixture
def corrupted_html():
    return """
    <html>
        <body>
            <table>
                <ul>
                    <li><a href='http://address.com/seller/ali' id='aa100'>Link 1</a></li>
                    <li><a href='http://address.com/seller/gholi' id='bb200'>Link 2</a></li>
                    <li><a href='http://address.com/seller/abbas' id='cc300'>Link 3</a></li>
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
    """


@pytest.fixture
def json_data():
    return {
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


def test_html_parser(html):
    html_parser = HTMLParser(html)
    parser = html_parser.parse(VeryNested)
    assert parser.items[0].items[0].id == 100
    assert parser.items[0].items[0].name == "Link 1"
    assert len(parser.items[0].items) == 3
    assert len(html_parser.resolver.urls) == 3
    assert str(html_parser.resolver.urls[2]) == "http://address.com/item?page=3"


def test_json_parser(json_data):
    json_parser = JsonParser(json_data)
    _json_parse_results = json_parser.parse(VeryNestedJson)
    assert len(_json_parse_results.results) == len(json_data["results"])
    assert _json_parse_results.results[0].id == json_data["results"][0]["id"]
    assert _json_parse_results.results[2].name == json_data["results"][2]["name"]
    assert len(json_parser.resolver.urls) == 1
    assert str(json_parser.resolver.urls[0]) == json_data["pagination"]["next_page"]


def test_exceptions_with_json_parser(json_data):
    json_data["results"][0]["id"] = "this is not int"
    json_parser = JsonParser(json_data)
    with pytest.raises(ParserValidationError):
        json_parser.parse(VeryNestedJson)

    class CustomClass:
        results: List[ListItemJson]
    with pytest.raises(ParserInvalidModelType):
        json_parser.parse(CustomClass)


def test_exceptions_with_html_parser(corrupted_html):
    html_parser = HTMLParser(corrupted_html)
    with pytest.raises(ParserValidationError):
        html_parser.parse(VeryNested)

    class CustomClass:
        results: List[ListItemJson]
    with pytest.raises(ParserInvalidModelType):
        html_parser.parse(CustomClass)
