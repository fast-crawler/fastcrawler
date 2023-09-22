from typing import Iterable, NamedTuple
from copy import copy
import asyncio

from .test_server import TestServer
from fastcrawler.engine.contracts import Request, Response, Url


class UrlInfo(NamedTuple):
    base_url: str
    route: str


class MockEngine:
    """This class uses the TestServer instance to handle requests and return responses.

    Attributes:
        servers (TestServer | Iterable[TestServer]): The test server instances.
        base_urls (str | Iterable[str]): The base urls of the requests.
    """

    def __init__(self, servers: TestServer | Iterable[TestServer], base_urls: str | Iterable[str]):
        servers = servers if not isinstance(servers, TestServer) else [servers]
        base_urls = base_urls if not isinstance(base_urls, str) else [base_urls]

        self.servers = {base_url: server for base_url, server in zip(base_urls, servers)}

    @staticmethod
    def _extract_base_url_and_route(url: str) -> UrlInfo:
        """Splits a URL into base URL and route.

        The base URL has the protocol, domain, and port (if any).
        The route has the rest of the URL.
        If the URL does not have "http" at the start,
        then the base URL is empty and the route is the whole URL.

        Args:
            url (str): The URL to be processed.

        Returns:
            UrlInfo: A tuple of the base URL and the route.
        """
        if url.startswith("http"):
            # Split the URL by "/" and take the first three elements
            base_url_parts = url.split("/", 3)[:3]
            # Join the base URL parts with "/"
            base_url = "/".join(base_url_parts)
            # Remove the base URL from the original URL to get the route
            route = url.replace(base_url, "")
        else:
            # If the URL does not start with "http", set the base URL to an empty string
            # and the route to the same as the URL
            base_url = ""
            route = url
        return UrlInfo(base_url, route)

    async def base(self, request: Request) -> Response:
        """The base method of the Engine protocol.

        This method uses the TestServer instance to get a response for a single request.

        Args:
            request (Request): The request to handle.

        Returns:
            Response: The response from the test server.
        """
        # Extract the base_url and route from Url
        base_url, route = self._extract_base_url_and_route(request.url)

        # Copy request parameters to prevent changing the original request parameters
        request_route = copy(request)
        request_route.url = route

        # Get the TestServer instance from the dictionary
        server = self.servers[base_url]

        # Get the response function from the test server
        response_func = server.get_response(request_route)

        # Get the response instance from the test server
        response_obj = (
            (await response_func) if asyncio.iscoroutine(response_func) else response_func
        )

        # Return the response object
        return response_obj

    async def batch(self, requests: Iterable[Request]) -> dict[Url, Response]:
        """The batch method of the Engine protocol.

        This method uses the TestServer instance to get a response for a list of requests.

        Args:
            requests (Iterable[Request]): The list of requests to handle.

        Returns:
            dict[Url, Response]: A dictionary mapping each url to its corresponding response.
        """
        tasks = []
        urls = []

        for request in requests:
            task = asyncio.create_task(self.base(request=request))
            tasks.append(task)
            urls.append(request.url)
            if request.sleep_interval:
                await asyncio.sleep(request.sleep_interval)

        results = await asyncio.gather(*tasks)
        return {Url(url): result for url, result in zip(urls, results)}
