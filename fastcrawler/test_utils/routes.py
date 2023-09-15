from typing import Any, Callable

from starlette.routing import NoMatchFound, compile_path

from fastcrawler.engine.contracts import Response
from fastcrawler.test_utils.endpoints import BaseEndpoint


class Route:
    """A class that represents a route for a request.

    This class can store a request pattern, a response object, and some helper attributes to match
    and handle requests.

    Attributes:
        request_pattern (str): The request pattern to match.
        response (BaseEndpoint): The response object to handle the request.
        path_regex (Pattern): The compiled regular expression for the request pattern.
        path_format (str): The formatted string for the request pattern.
        param_convertors (dict[str, Any]): The dict of param convertors for the request pattern.
    """

    def __init__(
        self,
        request_pattern: str,
        response: BaseEndpoint,
    ) -> None:
        """Initialize the route with a request pattern and a response object.

        Args:
            request_pattern (str): The request pattern to match.
            response (BaseEndpoint): The response object to handle the request.
        """
        self.request_pattern = request_pattern
        self.response = response
        self.path_regex, self.path_format, self.param_convertors = compile_path(request_pattern)

    def url_path_for(self, url: str, method: str) -> Callable[..., Response]:
        """Get a response for a given url and method.

        Args:
            url (str): The url to match.
            method (str): The method to match.

        Returns:
            Response: The response from the response object.

        Raises:
            NoMatchFound: If no match is found for the url and method.
        """
        match = self.path_regex.match(url)
        path_params: dict[str, Any] = {}
        if not match:
            raise NoMatchFound(url, path_params)

        matched_params = match.groupdict()
        for key, value in matched_params.items():
            matched_params[key] = self.param_convertors[key].convert(value)
        path_params.update(matched_params)
        method_func = self.response.dispatch(method.lower())
        return method_func(url, params=path_params)
