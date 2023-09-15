from pathlib import Path
from typing import Mapping, Any, NamedTuple

from fastcrawler.test_utils import (
    BaseEndpoint,
    Route,
    StaticResponse,
    SimpleResponse,
    HTMLPath,
    HTMLPathType,
)
from fastcrawler.engine.contracts import Response, Request, HTTPMethod


class Homepage(BaseEndpoint):
    async def get(self, request, *args, **kwargs):
        return Response(text="Hello, world!", status_code=200)


class User(BaseEndpoint):
    async def get(self, request, *args, params=None, **kwargs):
        params = params or {}
        text = "Hello"
        if user_id := params.get("user_id"):
            text += f", {user_id}"
        if post_id := params.get("post_id"):
            text += f" in {post_id}"
        if allow := params.get("allow"):
            text += f", allow is {allow}"
        if query := params.get("query"):
            text += f", query for {query}"
        return Response(text=text, status_code=200)


def read_html_file(html_file: HTMLPathType):
    with open(html_file) as html:
        html_content = html.read()
    return html_content


html_file = HTMLPath(Path(__file__).parent / "sample_html_file.html")


routes = [
    Route("/", Homepage()),
    Route("/user/{user_id}/{post_id}?allow={allow}&q={query}", User()),
    Route("/user/{user_id}", User()),
    Route("/html_file", StaticResponse(html_file, status_code=200)),
    Route("/simple", SimpleResponse(method=HTTPMethod.GET, status_code=201)),
    Route("/more_simple", SimpleResponse(method="GET", status_code=200)),
]

BASE_URL = "http://www.example.com"


class TestRequest(NamedTuple):
    http_request: Request  # The HTTP request object to be tested
    expected_response_attributes: Mapping[
        str, Any
    ]  # The expected attrs of the HTTP response object, such as status code, headers, text, etc.


test_requests = [
    TestRequest(
        Request(url=f"{BASE_URL}/user/123/3?allow=all&q=username", method=HTTPMethod.GET),
        {"status_code": 200, "text": "Hello, 123 in 3, allow is all, query for username"},
    ),
    TestRequest(
        Request(url=f"{BASE_URL}/user/123", method=HTTPMethod.GET),
        {"status_code": 200, "text": "Hello, 123"},
    ),
    TestRequest(
        Request(url=f"{BASE_URL}/", method=HTTPMethod.GET),
        {"status_code": 200, "text": "Hello, world!"},
    ),
    # TestRequest(
    #     Request(url=f"{BASE_URL}/", method=HTTPMethod.POST),
    #     {"status_code": 405, "text": "Method Not Allowed"},
    # ),
    TestRequest(
        Request(url=f"{BASE_URL}/html_file", method=HTTPMethod.GET),
        {"status_code": 200, "text": read_html_file(html_file)},
    ),
    TestRequest(
        Request(url=f"{BASE_URL}/simple", method=HTTPMethod.GET),
        {"status_code": 201},
    ),
    TestRequest(
        Request(url=f"{BASE_URL}/more_simple", method=HTTPMethod.GET),
        {"status_code": 200},
    ),
]
