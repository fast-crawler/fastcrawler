# from starlette.endpoints import HTTPEndpoint
from typing import Any
from functools import partial

from fastcrawler.engine.contracts import Response


async def not_allowed(*args, headers, **kwargs):
    return Response(text="Method Not Allowed", status_code=405, headers=headers)


class HTTPEndpoint:
    def __init__(self) -> None:
        self._allowed_methods = [
            method
            for method in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
            if getattr(self, method.lower(), None) is not None
        ]

    def dispatch(self, __name: str) -> Any:
        if resp := self.method_not_allowed(__name):
            return resp
        return getattr(self, __name)

    def method_not_allowed(self, scope: str) -> Response:
        # If we're running inside a starlette application then raise an
        # exception, so that the configurable exception handler can deal with
        # returning the response. For plain ASGI apps, just return the response.
        headers = {"Allow": ", ".join(self._allowed_methods)}
        if scope.upper() not in self._allowed_methods:
            return partial(not_allowed, headers=headers)
