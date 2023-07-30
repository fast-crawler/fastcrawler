import asyncio
from typing import Any

from aiohttp import BasicAuth, ClientSession, TCPConnector
from aiohttp.client import ClientResponse
from aiohttp.cookiejar import Morsel

from .contracts import ProxySetting, Request, RequestCycle, Response, SetCookieParam


class AioHttpEngine:
    default_request_limit = 1
    request_cls = Request
    response_cls = Response

    def __init__(
        self,
        cookies: list[SetCookieParam] | None = None,
        headers: dict | None = None,
        user_agent: str | None = None,
        proxy: ProxySetting | None = None,
        connection_limit: int | None = None,
    ):
        """Initialize a new engine instance with given cookie, header, user_agent, and proxy"""
        self.session: None | ClientSession = None
        self._cookies = (
            [(cookie.name, self._get_morsel_cookie(cookie)) for cookie in cookies]
            if cookies is not None
            else None
        )

        self._headers = headers or {}
        if user_agent:
            self._headers["User-Agent"] = user_agent

        self._connector = TCPConnector(
            limit_per_host=connection_limit or self.default_request_limit
        )

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
        cookie_params = {
            "name": cookie.key,
            "value": cookie.value,
            "domain": cookie.get("domain"),
            "path": cookie.get("path"),
            "expires": cookie.get("expires"),
            "httpOnly": cookie.get("httponly"),
            "secure": cookie.get("secure"),
            "sameSite": cookie.get("samesite"),
        }
        return SetCookieParam(**cookie_params)

    async def __aenter__(self) -> "AioHttpEngine":
        """Async context manager support for engine -> ENTER"""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager support for engine -> EXIT"""
        await self.teardown()
        return None

    async def setup(self, **kwargs) -> None:
        """Set-up up the engine for crawling purpose."""
        self.session = ClientSession(
            connector=self._connector,
            cookies=self._cookies,
            headers=self.headers,
            trust_env=True,
            **kwargs,
        )
        return None

    async def teardown(self) -> None:
        """Cleans up the engine."""
        if self.session:
            await self.session.close()
        return None

    async def base(
        self,
        request: Request,
        verify_ssl=False,
    ) -> RequestCycle | None:
        """Base Method for protocol to retrieve a list of URL."""
        if self.session:
            if isinstance(request.data, dict):
                json = request.data
                data = None
            else:
                json = None
                data = request.data

            async with self.session.request(
                request.method,
                request.url,
                json=json,
                data=data,
                headers=request.headers or self.headers,
                cookies=self._get_morsel_cookie(request.cookies)
                if request.cookies
                else self.cookies,
                verify_ssl=verify_ssl,
                **self._proxy,
            ) as response:
                return await self.translate_to_response(response, request)
        return None

    async def batch(self, requests: list[Request], method: str) -> dict[str, RequestCycle]:
        """Batch Method for protocol to retrieve a list of URL."""
        for request in requests:
            request.method = method
        tasks = []
        urls = []

        for request in requests:
            task = asyncio.create_task(self.base(request=request))
            tasks.append(task)
            urls.append(request.url)
            if request.sleep_interval:
                await asyncio.sleep(request.sleep_interval)

        results = await asyncio.gather(*tasks)
        return {url: result for url, result in zip(urls, results)}

    async def get(self, requests: list[Request]) -> dict[str, RequestCycle]:
        """GET HTTP Method for protocol to retrieve a list of URL."""
        return await self.batch(requests, "GET")

    async def post(self, requests: list[Request]) -> dict[str, RequestCycle]:
        """POST HTTP Method for protocol to crawl a list of URL."""
        return await self.batch(requests, "POST")

    async def put(self, requests: list[Request]) -> dict[str, RequestCycle]:
        """PUT HTTP Method for protocol to crawl a list of URL."""
        return await self.batch(requests, "PUT")

    async def delete(self, requests: list[Request]) -> dict[str, RequestCycle]:
        """DELETE HTTP Method for protocol to crawl a list of URL."""
        return await self.batch(requests, "DELETE")

    async def translate_to_response(
        self, response_obj: ClientResponse, request: Request
    ) -> RequestCycle:
        """Translate aiohttp response object to Response object"""
        response = self.response_cls(
            text=await response_obj.text(),
            status_code=response_obj.status,
            headers=response_obj.headers,
            cookies=response_obj.cookies,
            url=str(response_obj.url),
            id=str(request.url),
        )
        return RequestCycle(response=response, request=request)
