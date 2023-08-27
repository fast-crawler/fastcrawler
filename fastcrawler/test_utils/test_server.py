import asyncio
from typing import Mapping, Any
from typing import NamedTuple
from fastcrawler.engine.contracts import Request, Response

from fastcrawler.test_utils.routes import Route, NoMatchFound
from fastcrawler.test_utils.endpoint import HTTPEndpoint


class TestServer:
    def __init__(self, routes: list[Route] = None):
        self.routes = routes or []

    def add_route(self, route: Route):
        self.routes.append(route)

    def get_response(self, request: Request) -> Response:
        for route in self.routes:
            try:
                return route.url_path_for(request.url, request.method)
            except NoMatchFound:
                pass
        raise NoMatchFound(request.url, {})


# prepare a sample test request to test server


class Homepage(HTTPEndpoint):
    async def get(self, request, *args, **kwargs):
        return Response(text="Hello, world!", status_code=200)


class User(HTTPEndpoint):
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


routes = [
    Route("/", Homepage),
    Route("/user/{user_id}/{post_id}?allow={allow}&q={query}", User),
    Route("/user/{user_id}", User),
]


test_server = TestServer(routes=routes)


class TestRequest(NamedTuple):
    request: Request
    attrs: Mapping[str, Any]


# Create a request object with a specific value for the user_id placeholder
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
]


for test_request in test_requests:
    # Get the response from the test server
    test_response = asyncio.run(test_server.get_response(test_request.request))
    # Verify that the response is as expected
    print(test_request.request)
    for attr, val in test_request.attrs.items():
        assert getattr(test_response, attr) == val
        print(f"  :: {attr!r} == {val!r} -- Passed!")
