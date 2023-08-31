import os
from typing import Any
from functools import partial

import aiofiles
from fastcrawler.engine.contracts import Response


async def not_allowed(*args, headers, text="Method Not Allowed", **kwargs):
    return Response(text=text, status_code=405, headers=headers)


class HTTPEndpoint:
    def __init__(self) -> None:
        self._allowed_methods = [
            method
            for method in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
            if getattr(self, method.lower(), None) is not None
        ]

    def dispatch(self, request_method: str) -> Any:
        if resp := self.method_not_allowed(request_method):
            return resp
        return getattr(self, request_method)

    def method_not_allowed(self, scope: str) -> Response:
        # If we're running inside a starlette application then raise an
        # exception, so that the configurable exception handler can deal with
        # returning the response. For plain ASGI apps, just return the response.
        headers = {"Allow": ", ".join(self._allowed_methods)}
        if scope.upper() not in self._allowed_methods:
            return partial(not_allowed, headers=headers)


class HTMLResponse(HTTPEndpoint):
    def __init__(self, file: os.PathLike | str, **response_kwargs):
        super().__init__()
        self.file = file
        self.response_kwargs = response_kwargs

    async def get(self, *args, **kwargs) -> Response:
        content = await self.get_content()
        return Response(text=content, **self.response_kwargs)

    async def get_content(self) -> str:
        if isinstance(self.file, os.PathLike):
            # Convert the PathLike object to a str
            file_name = str(self.file)
        else:
            # Assume the file is a str
            file_name = self.file

        # Check if the file name is valid and is an html file
        if self.is_valid_file_name(file_name):
            async with aiofiles.open(file_name, "r") as f:
                content = await f.read()
            return content
        else:
            raise ValueError("Invalid file name or file type")

    def is_valid_file_name(self, file_name: str) -> bool:
        return os.path.exists(file_name) and file_name.endswith(".html")
