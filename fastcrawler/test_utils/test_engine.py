from typing import Iterable
from copy import copy
import asyncio

from pydantic import AnyUrl
from fastcrawler.engine.contracts import Request, Response, Url


from .test_server import TestServer


class MockEngine:
    """This class uses the TestServer instance to handle requests and return responses.

    Attributes:
        test_servers (Iterable[TestServer]): The test server instances.
        base_urls (Iterable[str]): The base urls of the requests.
    """

    def __init__(self, test_servers: Iterable[TestServer], base_urls: Iterable[str]):
        self.test_servers_map = {
            base_url: server for base_url, server in zip(base_urls, test_servers)
        }

    @classmethod
    def from_servers(mock_engine_cls, test_server_dict: dict[str, TestServer]):
        """Create a new instance of MockEngine

        Attributes:
            test_server_dict (dict[str, TestServer]): The test server instances in the dictionary
            The keys in the dictionary are the base_urls of the TestServer instances
        """
        return mock_engine_cls(
            test_servers=test_server_dict.values(), base_urls=test_server_dict.keys()
        )

    async def base(self, request: Request) -> Response:
        """The base method of the Engine protocol.

        This method uses the TestServer instance to get a response for a single request.

        Args:
            request (Request): The request to handle.

        Returns:
            Response: The response from the test server.
        """
        # Extract the base_url and route from Url
        request_url = AnyUrl(request.url)
        base_url, route = (
            f"{request_url.scheme}://{request_url.host}",
            f"{request_url.path}"
            + (f"?{request_url.query}" if request_url.query is not None else ""),
        )

        # Copy request parameters to prevent changing the original request parameters
        request_route = copy(request)
        request_route.url = route

        # Get the TestServer instance from the dictionary
        server = self.test_servers_map[base_url]

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
