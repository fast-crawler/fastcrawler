from typing import Optional, Callable

from fastcrawler.engine.contracts import Request, Response
from fastcrawler.test_utils.routes import Route, NoMatchFound


class TestServer:
    """A class that represents a test server.

    This class can store a list of routes and return a response for a given request.

    Attributes:
        routes (list[Route]): A list of routes that the server can handle.
    """

    def __init__(self, routes: Optional[list[Route]] = None) -> None:
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

        if response_function is None:
            raise NoMatchFound(request.url, {})
        # Otherwise, return the response from the route
        return response_function

    def _find_response_function(self, url: str, method: str) -> Callable[..., Response] | None:
        """Find a matching route for a given url and method.

        Args:
            url (str): The url to match.
            method (str): The method to match.

        Returns:
            Optional[Route]: The matching route or None if not found.
        """
        # Loop through the routes and return the first response that matches
        for route in self.routes:
            try:
                return route.url_path_for(url, method)
            except NoMatchFound:
                pass
        # If no route matches, return None
        return None
