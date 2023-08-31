import os
from typing import Any, Coroutine, Callable
from functools import partial

import aiofiles
from fastcrawler.engine.contracts import Response

from .utils import HTTPMethod


class HTMLPath(str):
    def __new__(cls, file_name):
        if not isinstance(file_name, (os.PathLike, str)):
            raise TypeError("Invalid html_file input format")

        file_name = str(file_name)
        if not (os.path.exists(file_name) and file_name.endswith(".html")):
            raise ValueError(f"{file_name} is not a valid HTML file")
        return file_name


async def not_allowed(*args, headers, text="Method Not Allowed", **kwargs) -> Response:
    return Response(text=text, status_code=405, headers=headers)


class BaseEndpoint:
    def __init__(self) -> None:
        self._allowed_methods = [
            method
            for method in [str(member) for member in HTTPMethod.__members__.values()]
            if getattr(self, method.lower(), None) is not None
        ]

    def dispatch(self, request_method: str) -> Any:
        if resp := self.method_not_allowed(request_method):
            return resp
        return getattr(self, request_method)

    def method_not_allowed(
        self, scope: str
    ) -> Callable[..., Coroutine[Any, Any, Response]] | None:
        # If we're running inside a starlette application then raise an
        # exception, so that the configurable exception handler can deal with
        # returning the response. For plain ASGI apps, just return the response.
        headers = {"Allow": ", ".join(self._allowed_methods)}
        if scope.upper() not in self._allowed_methods:
            return partial(not_allowed, headers=headers)
        return None


class StaticResponse(BaseEndpoint):
    def __init__(self, html_file: os.PathLike | str, **response_kwargs):
        super().__init__()
        self.html_file = HTMLPath(html_file)
        self.response_kwargs = response_kwargs

    async def get(self, *args, **kwargs) -> Response:
        content = await self.get_content()
        return Response(text=content, **self.response_kwargs)

    async def get_content(self) -> str:
        async with aiofiles.open(self.html_file, "r") as html_file:
            content = await html_file.read()
        return content


class DynamicResponse(BaseEndpoint):
    def __init__(self, method: HTTPMethod | str, **response_kwargs):
        async def http_method(self, *args, **kwargs):
            return Response(**response_kwargs)

        if method.upper() not in HTTPMethod.__members__:
            raise ValueError("method must be a member of HTTPMethod")

        setattr(self, method.lower(), http_method)
        super().__init__()
