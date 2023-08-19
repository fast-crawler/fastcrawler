# pragma: no cover
# pylint: disable=pointless-string-statement

from dataclasses import dataclass
from typing import Any, Literal, NewType, Protocol

import pydantic


@dataclass
class SetCookieParam:
    name: str = ""
    value: str = ""
    url: str | None = None
    domain: str = ""
    path: str = ""
    expires: str = ""
    httpOnly: str = ""
    secure: str = ""
    sameSite: str | Literal["Lax", "None", "Strict"] = ""


@dataclass
class ProxySetting:
    server: str
    port: int
    username: str | None = None
    password: str | None = None
    protocol: str = "http://"


@dataclass
class Response:
    id: str | None = None
    text: str | None = None
    status_code: int | None = None
    headers: dict | None = None
    cookies: SetCookieParam | None = None
    url: str | None = None


@dataclass
class Request:
    url: str
    proxy: ProxySetting | None = None
    data: dict | str | None = None
    method: str | None = None
    headers: dict | None = None
    cookies: SetCookieParam | None = None
    sleep_interval: float | None = None


@dataclass
class RequestCycle:
    request: Request
    response: Response
    parsed_data: Any | pydantic.BaseModel | None = None


Url = NewType("Url", str)


class EngineProto(Protocol):
    default_request_limit: int

    def __init__(
        self,
        cookies: list[SetCookieParam] | None = None,
        headers: dict | None = None,
        useragent: str | None = None,
        proxy: ProxySetting | None = None,
        connection_limit: int = 100,
    ):
        "Initialize a new engine instance with given cookie(s), header(s), useragent, and proxy"

    @property
    def cookies(self) -> list[SetCookieParam] | None:
        """Return cookies of the session"""

    @property
    def headers(self) -> dict:  # type: ignore
        """Return headers of the session"""

    @property
    def proxy(self) -> ProxySetting | None:
        """Return proxy setting of the session"""

    async def __aenter__(self) -> "EngineProto":  # type: ignore
        """Async context manager support for engine -> ENTER"""

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager support for engine -> EXIT"""

    async def setup(self) -> None:
        """Set-up up the engine for crawling purpose."""

    async def teardown(self) -> None:
        """Cleans up the engine."""

    async def base(
        self,
        request: Request,
        verify_ssl=False,
    ) -> RequestCycle | None:
        """Base Method for protocol to retrieve a list of URL."""

    async def batch(
        self,
        requests: list[Request],
        method: str,
    ) -> dict[Url, RequestCycle]:  # type: ignore
        """Batch Method for protocol to retrieve a list of URL."""

    async def get(
        self,
        requests: list[Request],
    ) -> dict[Url, RequestCycle]:  # type: ignore
        """GET HTTP Method for protocol to retrieve a list of URL."""

    async def post(
        self,
        requests: list[Request],
    ) -> dict[Url, RequestCycle]:  # type: ignore
        """POST HTTP Method for protocol to crawl a list of URL."""

    async def put(
        self,
        requests: list[Request],
    ) -> dict[Url, RequestCycle]:  # type: ignore
        """PUT HTTP Method for protocol to crawl a list of URL."""

    async def delete(
        self,
        requests: list[Request],
    ) -> dict[Url, RequestCycle]:  # type: ignore
        """DELETE HTTP Method for protocol to crawl a list of URL."""

    async def translate_to_response(
        self,
        response_obj: Any,
        request: Request,
    ) -> RequestCycle:  # type: ignore
        """Translate the response object to a Response object"""
