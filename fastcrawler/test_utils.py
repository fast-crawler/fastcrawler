from enum import StrEnum
import re
from typing import Callable, Dict, Tuple

from fastcrawler.engine.contracts import (
    ProxySetting,
    RequestCycle,
    SetCookieParam,
    Response,
    Url,
    Request,
    # EngineProto,
)


class Method(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class MockEngine:
    def __init__(
        self,
        cookies: list[SetCookieParam] | None = None,
        headers: dict | None = None,
        user_agent: str | None = None,
        proxy: ProxySetting | None = None,
        connection_limit: int | None = None,
    ):
        ...

    async def batch(
        self,
        requests: list[Request],
        method: str,
    ) -> dict[Url, RequestCycle]:  # type: ignore
        """Batch Method for protocol to retrieve a list of URL."""
        return ...

    async def get(self, requests: list[Request]) -> dict[Url, RequestCycle]:
        """GET HTTP Method for protocol to retrieve a list of URL."""
        return await self.batch(requests, "GET")

    async def post(self, requests: list[Request]) -> dict[Url, RequestCycle]:
        """POST HTTP Method for protocol to crawl a list of URL."""
        return await self.batch(requests, "POST")

    async def put(self, requests: list[Request]) -> dict[Url, RequestCycle]:
        """PUT HTTP Method for protocol to crawl a list of URL."""
        return await self.batch(requests, "PUT")

    async def delete(self, requests: list[Request]) -> dict[Url, RequestCycle]:
        """DELETE HTTP Method for protocol to crawl a list of URL."""
        return await self.batch(requests, "DELETE")


class TestServer:
    def __init__(self, default_response: Callable[[Request], Response]):
        self.default_response = default_response
        self.responses: Dict[Tuple[str, str], Callable[[Request], Response]] = {}

    def add_response(self, request: Request, response: Callable[[Request], Response]):
        # Extract the names of the placeholders from the URL pattern
        placeholder_names = re.findall(r"{([^}]+)}", request.url)

        # Convert the URL pattern to a regular expression
        url_pattern = request.url
        for name in placeholder_names:
            url_pattern = url_pattern.replace(f"{{{name}}}", f"(?P<{name}>[^/]+)")

        self.responses[(f"{request.method}", url_pattern)] = response

    def get_response(self, request: Request) -> Response:
        for (method, url_pattern), response in self.responses.items():
            match = re.fullmatch(url_pattern, request.url)
            if method == f"{request.method}" and match:
                return response(request)
        return self.default_response(request)


def default_response(request: Request) -> Response:
    return Response(text="404 not found", status_code=404)


def user_details_response(request: Request) -> Response:
    # Extract the user_id from the request URL
    user_id = re.search(r"/user/([^/]+)", request.url).group(1)
    return Response(text=f"User {user_id}", status_code=200)


# Create a test server instance with a default response
test_server = TestServer(default_response=default_response)

# Create a request object with a URL pattern that includes a placeholder
request = Request(url="/user/{user_id}", method="GET")

# Add the user_details_response to the test server
test_server.add_response(request, user_details_response)

# Create a request object with a specific value for the user_id placeholder
test_request = Request(url="/user/123", method="GET")

# Get the response from the test server
test_response = test_server.get_response(test_request)

# Verify that the response is as expected
assert test_response.status_code == 200
assert test_response.text == "User 123"
