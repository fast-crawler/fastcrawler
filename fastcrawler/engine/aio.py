import asyncio
from typing import Any

import pydantic
from aiohttp import BasicAuth, ClientSession, TCPConnector
from aiohttp.cookiejar import Morsel

from fastcrawler.engine.contracts import ProxySetting, SetCookieParam


class AioHttpEngine:
    def __init__(
        self,
        cookies: list[SetCookieParam] | None = None,
        headers: dict | None = None,
        useragent: str | None = None,
        proxy: ProxySetting | None = None,
        connection_limit: int = 100,
    ):
        """Initialize a new engine instance with given cookie, header, useragent, and proxy"""
        self.session: None | ClientSession = None
        self._cookies = (
            [(cookie.name, self._get_morsel_cookie(cookie)) for cookie in cookies]
            if cookies is not None
            else None
        )

        self._headers = headers or {}
        if useragent:
            self._headers["User-Agent"] = useragent

        self._connector = TCPConnector(limit_per_host=connection_limit)

        self._proxy: dict[Any, Any] = {}
        self.proxy_dct = proxy
        if proxy:
            proxy_url = f"{proxy.protocol}{proxy.server}:{proxy.port}"
            self._proxy["proxy"] = proxy_url
            if proxy.username and proxy.password:
                self._proxy["proxy_auth"] = BasicAuth(
                    login=proxy.username, password=proxy.password
                )

    @property
    def cookies(self) -> list[SetCookieParam] | None:
        """Return cookies"""
        cookies = None
        if self._cookies is not None:
            cookies = [self._get_cookie(cookie) for _, cookie in self._cookies]

        return cookies

    @property
    def headers(self) -> dict:
        """Return headers"""
        return self._headers

    @property
    def proxy(self) -> ProxySetting | None:
        """Return proxy setting"""
        return self.proxy_dct

    @staticmethod
    def _get_morsel_cookie(cookie: SetCookieParam) -> Morsel:
        """Converts a SetCookieParam object to an Morsel object."""
        morsel_obj: Morsel = Morsel()
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

    @staticmethod
    def _get_cookie(cookie: Morsel) -> SetCookieParam:
        """convert Morsel object to SetCookieParam object"""
        trans = {
            "domain": "domain",
            "path": "path",
            "expires": "expires",
            "httponly": "httpOnly",
            "secure": "secure",
            "samesite": "sameSite",
        }
        cookie_params = {
            "name": cookie.key,
            "value": cookie.value,
        }
        cookie_params.update(
            {
                v: cookie.get(k, "")
                for k, v in trans.items()
                if v is not None and cookie.get(k) is not None
            }
        )
        return SetCookieParam(**cookie_params)

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
            cookies=self._cookies,
            headers=self.headers,
            trust_env=True,
            **kwargs,
        )

    async def teardown(self) -> None:
        """Cleans up the engine."""
        if self.session:
            await self.session.close()

    async def base(
        self, url: pydantic.AnyUrl, method: str, data: dict | None, **kwargs
    ) -> str | None:
        """Base Method for protocol to retrieve a list of URL."""
        if self.session:
            async with self.session.request(
                method, str(url), data=data, headers=self.headers, **self._proxy, **kwargs
            ) as response:
                return await response.text()
        return None

    async def get(self, urls: list[pydantic.AnyUrl], **kwargs) -> list[str] | str:
        """GET HTTP Method for protocol to retrieve a list of URL."""
        tasks = [self.base(url, "GET", None, **kwargs) for url in urls]
        return await asyncio.gather(*tasks)

    async def post(
        self, urls: list[pydantic.AnyUrl], datas: list[dict], **kwargs
    ) -> list[str] | str:
        """POST HTTP Method for protocol to crawl a list of URL."""
        tasks = [self.base(url, "POST", data=data, **kwargs) for url, data in zip(urls, datas)]
        return await asyncio.gather(*tasks)

    async def put(
        self, urls: list[pydantic.AnyUrl], datas: list[dict], **kwargs
    ) -> list[str] | str:
        """PUT HTTP Method for protocol to crawl a list of URL."""
        tasks = [self.base(url, "PUT", data=data, **kwargs) for url, data in zip(urls, datas)]
        return await asyncio.gather(*tasks)

    async def delete(
        self, urls: list[pydantic.AnyUrl], datas: list[dict], **kwargs
    ) -> list[str] | str:
        """DELETE HTTP Method for protocol to crawl a list of URL."""
        tasks = [self.base(url, "DELETE", data=data, **kwargs) for url, data in zip(urls, datas)]
        return await asyncio.gather(*tasks)
