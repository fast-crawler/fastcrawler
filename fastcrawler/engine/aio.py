import asyncio

import pydantic
from aiohttp import BasicAuth, ClientSession, TCPConnector
from aiohttp.cookiejar import Morsel

from fastcrawler.engine.base import EngineProto, ProxySetting, SetCookieParam


class AioHTTP(EngineProto):
    def __init__(
        self,
        cookies: list[SetCookieParam] | None = None,
        headers: dict | None = None,
        useragent: str | None = None,
        proxy: ProxySetting | None = None,
        connection_limit: int = 100,
    ):
        """Initialize a new engine instance with given cookie, header, useragent, and proxy"""
        self.session = None

        self._cookies = (
            [(cookie.name, self.get_morsel_cookie(cookie)) for cookie in cookies] if cookies is not None else None
        )

        self._headers = headers or {}
        if useragent:
            self._headers["User-Agent"] = useragent

        self._connector = TCPConnector(limit_per_host=connection_limit)

        self._proxy = {}
        if proxy:
            proxy_url = f"{proxy.protocol}{proxy.server}:{proxy.port}"
            self._proxy["proxy"] = proxy_url
            if proxy.username and proxy.password:
                auth = BasicAuth(login=proxy.username, password=proxy.password)
                self._proxy["proxy_auth"] = auth

    @property
    def cookies(self):
        return self._cookies

    @property
    def headers(self):
        return self._headers

    @property
    def proxy(self):
        return self._proxy

    def get_morsel_cookie(self, cookie: SetCookieParam) -> Morsel:
        """Converts a SetCookieParam object to an Morsel object."""
        morsel_obj = Morsel()
        morsel_obj.set(cookie.name, cookie.value, cookie.value)
        morsel_obj.update(
            dict(
                domain=cookie.domain,
                path=cookie.path,
                expires=cookie.expires,
                secure=cookie.secure,
                httponly=cookie.httpOnly,
                samesite=cookie.sameSite,
            )
        )
        return morsel_obj

    async def __aenter__(self):
        """Async context manager support for engine -> ENTER"""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager support for engine -> EXIT"""
        await self.teardown()

    async def setup(self, **kwargs) -> None:
        """Set-up up the engine for crawling purpose."""
        self.session = ClientSession(
            connector=self._connector,
            cookies=self.cookies,
            headers=self.headers,
            trust_env=True,
            **kwargs,
        )


    async def teardown(self) -> None:
        """Cleans up the engine."""
        await self.session.close()

    async def base(self, url: pydantic.AnyUrl, method: str, data: dict, **kwargs) -> str:
        """Base Method for protocol to retrieve a list of URL."""

        async with self.session.request(
            method, url, data=data, headers=self.headers, **self.proxy, **kwargs
        ) as response:
            return await response.text()

    async def get(self, urls: list[pydantic.AnyUrl], **kwargs) -> list[str] | str:
        """GET HTTP Method for protocol to retrieve a list of URL."""
        tasks = [self.base(url, "GET", None, **kwargs) for url in urls]
        return await asyncio.gather(*tasks)

    async def post(self, urls: list[pydantic.AnyUrl], datas: list[dict], **kwargs) -> list[str] | str:
        """POST HTTP Method for protocol to crawl a list of URL."""
        tasks = [self.base(url, "POST", data=data, **kwargs) for url, data in zip(urls, datas)]
        return await asyncio.gather(*tasks)

    async def put(self, urls: list[pydantic.AnyUrl], datas: list[dict], **kwargs) -> list[str] | str:
        """PUT HTTP Method for protocol to crawl a list of URL."""
        tasks = [self.base(url, "PUT", data=data) for url, data in zip(urls, datas)]
        return await asyncio.gather(*tasks)

    async def delete(self, urls: list[pydantic.AnyUrl], datas: list[dict], **kwargs) -> list[str] | str:
        """DELETE HTTP Method for protocol to crawl a list of URL."""
        tasks = [self.base(url, "DELETE", data=data, **kwargs) for url, data in zip(urls, datas)]
        return await asyncio.gather(*tasks)
