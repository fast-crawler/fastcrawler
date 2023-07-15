# pylint: skip-file
import pytest

from test.shared.schema import (
    EmailData,
    InnerHTML,
    LinksData,
    LinksDataSingle,
    ListItemJson,
    NotSupportedProcessor,
    VeryNested,
    VeryNestedCSS,
    VeryNestedJson,
)
from fastcrawler.exceptions import (
    ParserInvalidModelType,
    ParserValidationError,
    ProcessorNotSupported,
)
from fastcrawler.parsers import HTMLParser, JsonParser
from fastcrawler.parsers.selectors.base import BaseSelector
from fastcrawler.parsers.utils import _UNSET


def test_html_parser_with_xpath(html):
    html_parser = HTMLParser(html)
    parser = html_parser.parse(VeryNested)
    print(parser.items)
    assert len(parser.items[0].items) == 3
    assert parser.items[0].items[0].id == 100
    assert parser.items[0].items[0].name == "Link 1"
    assert parser.items[0].items[2].name == "Link 3"
    assert parser.items[0].items[2].source_as_default == "Nothing"
    assert len(html_parser.resolver.urls) == 3
    assert str(html_parser.resolver.urls[2]) == "http://address.com/item?page=3"


def test_html_parser_with_css(html):
    html_parser = HTMLParser(html)
    parser = html_parser.parse(VeryNestedCSS)
    assert len(parser.items[0].items) == 3
    assert parser.items[0].items[0].id == 100
    assert parser.items[0].items[0].name == "Link 1"
    assert parser.items[0].items[2].name == "Link 3"
    assert parser.items[0].items[2].source_as_default == "Nothing"
    assert len(html_parser.resolver.urls) == 3
    assert str(html_parser.resolver.urls[2]) == "http://address.com/item?page=3"


def test_get_inner_html(html):
    html_parser = HTMLParser(html)
    parser = html_parser.parse(InnerHTML)
    assert "<table>" in parser.table
    assert "<li" in parser.table
    assert "<nav>" not in parser.table


def test_get_no_html():
    html = "nothing here"
    html_parser = HTMLParser(html)
    parser = html_parser.parse(InnerHTML)
    assert parser.table is None


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
        results: list[ListItemJson]

    with pytest.raises(ParserInvalidModelType):
        json_parser.parse(CustomClass)


def test_exceptions_with_html_parser(corrupted_html):
    html_parser = HTMLParser(corrupted_html)
    with pytest.raises(ParserValidationError):
        html_parser.parse(VeryNested)

    class CustomClass:
        results: list[ListItemJson]

    with pytest.raises(ParserInvalidModelType):
        html_parser.parse(CustomClass)


def test_base_selector():
    obj = BaseSelector("Test", many=True)
    with pytest.raises(NotImplementedError):
        obj.resolve(None, None)
    assert obj.__repr__() == "Field(type=BaseSelector extract=None, many=True, query=Test)"


def test_regex_path(html: str):
    html_parser = HTMLParser(html)
    parser = html_parser.parse(LinksData)
    assert len(parser.link) == html.count("href")

    html_parser = HTMLParser(html)
    _parser = html_parser.parse(LinksDataSingle)
    assert _parser.link == parser.link[0]

    html_parser = HTMLParser(html)
    parser = html_parser.parse(EmailData)
    assert parser.emails is None


def test_unset():
    assert bool(_UNSET) is False


def test_not_supported_processor(html):
    with pytest.raises(ProcessorNotSupported):
        html_parser = HTMLParser(html)
        html_parser.parse(NotSupportedProcessor)


# def test_html_parser_with_css_modest(html):
#     html_parser = HTMLParser(html)
#     parser = html_parser.parse(MDT_NestedItemList)
#     assert len(parser.items[0].items) == 3
#     assert parser.items[0].items[0].id == 100
#     assert parser.items[0].items[0].name == "Link 1"
#     assert parser.items[0].items[2].name == "Link 3"
#     assert parser.items[0].items[2].source_as_default == "Nothing"
#     assert len(html_parser.resolver.urls) == 3
#     assert str(html_parser.resolver.urls[2]) == "http://address.com/item?page=3"


# def test_html_parser_with_css_modest_flat(html):
#     html_parser = HTMLParser(html)
#     html_parser.parse(MDT_FlatList)
