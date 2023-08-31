from pathlib import Path
from typing import Mapping, Any, NamedTuple

from fastcrawler.test_utils import BaseEndpoint, Route, StaticResponse, DynamicResponse, HTTPMethod
from fastcrawler.engine.contracts import Response, Request


class Homepage(BaseEndpoint):
    async def get(self, request, *args, **kwargs):
        return Response(text="Hello, world!", status_code=200)


class User(BaseEndpoint):
    async def get(self, request, *args, params=None, **kwargs):
        params = params or {}
        user_id = params.get("user_id")
        post_id = params.get("post_id")
        allow = params.get("allow")
        query = params.get("query")
        text = "Hello"
        if user_id:
            text += f", {user_id}"
        if post_id:
            text += f" in {post_id}"
        if allow:
            text += f", allow is {allow}"
        if query:
            text += f", query for {query}"
        return Response(text=text, status_code=200)


def read_html_file(html_file):
    with open(html_file) as html:
        html_content = html.read()
    return html_content


html_file = Path(__file__).parent / "sample_html_file.html"


routes = [
    Route("/", Homepage()),
    Route("/user/{user_id}/{post_id}?allow={allow}&q={query}", User()),
    Route("/user/{user_id}", User()),
    Route("/html_file", StaticResponse(html_file, status_code=200)),
    Route("/simple", DynamicResponse(method=HTTPMethod.GET, status_code=201)),
    Route("/more_simple", DynamicResponse(method="GET", status_code=200)),
]


class TestRequest(NamedTuple):
    http_request: Request  # The HTTP request object to be tested
    expected_response_attributes: Mapping[
        str, Any
    ]  # The expected attrs of the HTTP response object, such as status code, headers, text, etc.


test_requests = [
    TestRequest(
        Request(url="/user/123/3?allow=all&q=username", method="GET"),
        {"status_code": 200, "text": "Hello, 123 in 3, allow is all, query for username"},
    ),
    TestRequest(
        Request(url="/user/123", method="GET"),
        {"status_code": 200, "text": "Hello, 123"},
    ),
    TestRequest(
        Request(url="/", method="GET"),
        {"status_code": 200, "text": "Hello, world!"},
    ),
    TestRequest(
        Request(url="/", method="POST"),
        {"status_code": 405, "text": "Method Not Allowed"},
    ),
    TestRequest(
        Request(url="/html_file", method="GET"),
        {"status_code": 200, "text": read_html_file(html_file)},
    ),
    TestRequest(
        Request(url="/simple", method="GET"),
        {"status_code": 201},
    ),
    TestRequest(
        Request(url="/more_simple", method="GET"),
        {"status_code": 200},
    ),
]
