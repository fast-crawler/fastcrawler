from typing import Callable

from fastcrawler.engine.contracts import Request, Response
from fastcrawler.test_utils.routes import Route, NoMatchFound


class TestServer:
    """A class that represents a test server.

    This class can store a list of routes and return a response for a given request.

    Attributes:
        routes (list[Route]): A list of routes that the server can handle.
    """

    def __init__(self, routes: list[Route] | None) -> None:
        self.routes = routes or []

    def add_route(self, route: Route) -> None:
        """Add a route to the server.

        Args:
            route (Route): The route to add.
        """
        self.routes.append(route)

    def get_response(self, request: Request) -> Callable[..., Response]:
        """Get a response for a given request.

        Args:
            request (Request): The request to handle.

        Returns:
            Response: The response function from the matching route.

        Raises:
            NoMatchFound: If no route matches the request.
        """
        assert request.method
        response_function = self._find_response_function(request.url, request.method)

        return response_function

    def _find_response_function(self, url: str, method: str) -> Callable[..., Response]:
        """Find a matching route for a given url and method.

        Args:
            url (str): The url to match.
            method (str): The method to match.

        Returns:
            Route: The matching route

        Raises:
            NoMatchFound: If no route matches the request.
        """
        # Loop through the routes and return the first response that matches
        for route in self.routes:
            try:
                return route.get_response_from_url(url, method)
            except NoMatchFound:
                pass
        raise NoMatchFound(url, {})
