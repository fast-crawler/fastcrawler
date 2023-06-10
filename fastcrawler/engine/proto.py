from typing import List, Protocol

import pydantic


class ProxySetting(pydantic.BaseModel):
    protocol: str = "http://"
    server: str
    port: int
    username: str | None = None
    password: str | None = None


class EngineProto(Protocol):
    def __init__(self, cookie: List[dict], header: dict, useragent: dict, proxy: ProxySetting): ...
    """ Initialize a new engine instance with given cookie, header, useragent, and proxy
    """
    async def __aenter__(self): ...
    """ Async context manager support for engine -> ENTER
    """
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
    """ Async context manager support for engine -> EXIT
    """
    async def setup(self) -> None: ...
    """ Set-up up the engine for crawling purpose.
    """
    async def teardown(self) -> None: ...
    """ Cleans up the engine.
    """
    async def base(self, url: pydantic.AnyUrl, data: dict) -> str: ...
    """ Base Method for protocol to retrieve a list of URL.
    """
    async def get(self, urls: List[pydantic.AnyUrl]) -> str: ...
    """ GET HTTP Method for protocol to retrieve a list of URL.
    """
    async def post(self, urls: List[pydantic.AnyUrl], datas: List[dict]) -> str: ...
    """ POST HTTP Method for protocol to crawl a list of URL.
    """
    async def put(self, urls: List[pydantic.AnyUrl], datas: List[dict]) -> str: ...
    """ POST HTTP Method for protocol to crawl a list of URL.
    """
    async def delete(self, urls: List[pydantic.AnyUrl], datas: List[dict]) -> str: ...
    """ DELETE HTTP Method for protocol to crawl a list of URL.
    """
