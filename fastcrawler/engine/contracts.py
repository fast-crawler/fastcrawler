# pragma: no cover
# pylint: disable=pointless-string-statement

from typing import Literal, Protocol

import pydantic


class SetCookieParam(pydantic.BaseModel):
    name: str = ""
    value: str = ""
    url: str | None = None
    domain: str = ""
    path: str = ""
    expires: str = ""
    httpOnly: str = ""
    secure: str = ""
    sameSite: str | Literal["Lax", "None", "Strict"] = ""


class ProxySetting(pydantic.BaseModel):
    protocol: str = "http://"
    server: str
    port: int
    username: str | None = None
    password: str | None = None


class Response(pydantic.BaseModel):
    text: str | None = None
    status_code: int | None = None
    headers: dict | None = None
    cookie: dict | None = None
    url: str | None = None


class Request(pydantic.BaseModel):
    url: str
    data: dict | str | None = None


class EngineProto(Protocol):
    default_request_limit: int

    def __init__(
        self,
        cookies: list[SetCookieParam] | None,
        headers: dict | None,
        useragent: str | None,
        proxy: ProxySetting | None,
        connection_limit: int = 100,
    ):
        "Initialize a new engine instance with given cookie(s), header(s), useragent, and proxy"

    async def __aenter__(self):
        """Async context manager support for engine -> ENTER"""

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager support for engine -> EXIT"""

    async def setup(self) -> None:
        """Set-up up the engine for crawling purpose."""

    async def teardown(self) -> None:
        """Cleans up the engine."""

    async def base(self, url: pydantic.AnyUrl, method: str, data: dict) -> str:
        """Base Method for protocol to retrieve a list of URL."""

    async def get(self, urls: list[pydantic.AnyUrl]) -> str:
        """GET HTTP Method for protocol to retrieve a list of URL."""

    async def post(self, urls: list[pydantic.AnyUrl], datas: list[dict]) -> str:
        """POST HTTP Method for protocol to crawl a list of URL."""

    async def put(self, urls: list[pydantic.AnyUrl], datas: list[dict]) -> str:
        """POST HTTP Method for protocol to crawl a list of URL."""

    async def delete(self, urls: list[pydantic.AnyUrl], datas: list[dict]) -> str:
        """DELETE HTTP Method for protocol to crawl a list of URL."""

    async def translate_to_response(self, response_obj: type) -> Response:
        """Translate the response object to a Response object"""
