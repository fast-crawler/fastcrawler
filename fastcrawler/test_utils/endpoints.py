import os
import json
from pathlib import Path
from typing import Any, Callable, Coroutine, Self, TypeVar
from functools import partial

import aiofiles
from fastcrawler.engine.contracts import Response, HTTPMethod


class FilePath(str):
    """A class that represents a valid HTML/Json file path.

    This class inherits from str and validates the input file name.

    Raises:
        TypeError: If the file name is not a string or a path-like object.
        ValueError: If the file name does not exist or does not end with ".html".
    """

    def __new__(cls, file_name: os.PathLike | str) -> Self:
        """Create a new HTMLPath object.

        Args:
            file_name (Union[os.PathLike, str]): The file name to validate.

        Returns:
            FilePath: The validated HTML/Json file path.
        """
        if not isinstance(file_name, (os.PathLike, str)):
            raise TypeError("Invalid file input format")

        file_name = str(file_name)
        if not (
            os.path.exists(file_name)
            and any([file_name.endswith(".html"), file_name.endswith(".json")])
        ):
            raise ValueError(f"{file_name} is not a valid HTML/Json file or not found!")
        return super().__new__(cls, file_name)


FilePathType = TypeVar("FilePathType", bound=FilePath)


async def not_allowed(
    *args, headers: dict, text: str = "Method Not Allowed", **kwargs
) -> Response:
    """Return a response with status code 405.

    Args:
        headers (dict): The headers to include in the response.
        text (str, optional): The text to include in the response.
        Defaults to "Method Not Allowed".

    Returns:
        Response: The response object with status code 405.
    """
    return Response(text=text, status_code=405, headers=headers)


class BaseEndpoint:
    """A base class that represents an HTTP endpoint.

    This class defines some common attributes and methods for handling HTTP requests.

    Attributes:
        _allowed_methods (list[str]): A list of allowed HTTP methods for this endpoint.
    """

    def __init__(self) -> None:
        """Initialize the base endpoint with the allowed methods."""
        self._allowed_methods = [
            method
            for method in [str(member) for member in HTTPMethod]
            if getattr(self, method.lower(), None) is not None
        ]

    def dispatch(
        self, request_method: str
    ) -> Coroutine[Any, Any, Response] | Callable[..., Response]:
        """Dispatch the request to the appropriate method.

        Args:
            request_method (str): The request method to dispatch.

        Returns:
            Any: The result of calling the corresponding method.
        """
        if resp := self.method_not_allowed(request_method):
            return resp
        return getattr(self, request_method)

    def method_not_allowed(
        self, scope: str
    ) -> Callable[..., Coroutine[Any, Any, Response]] | None:
        """Check if the request method is not allowed and return a not_allowed response.

        Args:
            scope (str): The request method to check.

        Returns:
            Union[Callable[..., Coroutine[Any, Any, Response]], None]:
            A coroutine function that returns a response with status code 405 if the method is
            not allowed, or None otherwise.
        """
        # If we're running inside a starlette application then raise an
        # exception, so that the configurable exception handler can deal with
        # returning the response. For plain ASGI apps, just return the response.
        headers = {"Allow": ", ".join(self._allowed_methods)}
        if scope.upper() not in self._allowed_methods:
            return partial(not_allowed, headers=headers)
        return None


class StaticResponse(BaseEndpoint):
    """A class that represents a static response.

    This class handles requests by returning the content of a HTML/Json file.

    Attributes:
        file_path (FilePathType): The file path to read from.
        response_kwargs (dict): The keyword arguments to pass to the response object.
        file_type (str): The type of the file ('html' or 'json').
    """

    def __init__(
        self, file_path: FilePathType, method: HTTPMethod | str = HTTPMethod.GET, **response_kwargs
    ) -> None:
        """Initialize the static response with a file and optional keyword arguments.

        Args:
            file_path (FilePathType): The file path to read from.
            method (Union[HTTPMethod, str]): The HTTP method to handle.
            **response_kwargs: The keyword arguments to pass to the response object.
        """
        setattr(self, method.lower(), self.http_method)
        super().__init__()
        self.file_path = Path(file_path)

        self.file_type = self.file_path.suffix.replace(".", "", 1).lower()
        self.response_kwargs = response_kwargs

    async def http_method(self, *args, **kwargs) -> Response:
        """Handle a request method and return a response with the content.

        Returns:
            Response: The response object with the content.
        """
        content = await self.get_content()
        return Response(text=content, **self.response_kwargs)

    async def get_content(self) -> str:
        """Read and return the content from the file.

        Returns:
            str: The content as a string.
        """
        async with aiofiles.open(self.file_path, "r") as file:
            if self.file_type == "html":
                content = await file.read()
            elif self.file_type == "json":
                content = json.dumps(json.loads(await file.read()))
            else:
                raise ValueError(f"Unsupported file type: {self.file_type}")

        return content


class SimpleResponse(BaseEndpoint):
    """A class that represents a simple response.

    This class inherits from BaseEndpoint and handles a single HTTP method by
    returning a response with the given keyword arguments.

    Attributes:
        response_kwargs (dict): The keyword arguments to pass to the response object.
    """

    def __init__(self, method: HTTPMethod | str, **response_kwargs) -> None:
        """Initialize the simple response with an HTTP method and optional keyword arguments.

        Args:
            method (Union[HTTPMethod, str]): The HTTP method to handle.
            **response_kwargs: The keyword arguments to pass to the response object.

        Raises:
            ValueError: If the method is not a member of HTTPMethod.
        """

        def http_method(self, *args, **kwargs) -> Response:
            """Handle the HTTP request and return a response with the given keyword arguments.

            Returns:
                Response: The response object with the given keyword arguments.
            """
            return Response(**response_kwargs)

        if method.upper() not in HTTPMethod.__members__:
            raise ValueError("method must be a member of HTTPMethod")

        setattr(self, method.lower(), http_method)
        super().__init__()
