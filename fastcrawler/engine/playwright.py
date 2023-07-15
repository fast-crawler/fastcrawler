# pragma: no cover
# noqa

import pydantic

from fastcrawler.engine.contracts import ProxySetting, SetCookieParam


class PlayWrightEngine:
    def __init__(
        self,
        cookies: list[SetCookieParam] | None = None,
        headers: dict | None = None,
        useragent: str | None = None,
        proxy: ProxySetting | None = None,
        connection_limit: int = 100,
    ):
        """Initialize a new engine instance with given cookie, header, useragent, and proxy"""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    @property
    def cookies(self):
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    @property
    def headers(self):
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    @property
    def proxy(self):
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    async def __aenter__(self):
        """Async context manager support for engine -> ENTER"""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager support for engine -> EXIT"""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    async def setup(self, **kwargs) -> None:
        """Set-up up the engine for crawling purpose."""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    async def teardown(self) -> None:
        """Cleans up the engine."""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    async def base(self, url: pydantic.AnyUrl, method: str, data: dict, **kwargs) -> str:
        """Base Method for protocol to retrieve a list of URL."""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    async def get(self, urls: list[pydantic.AnyUrl], **kwargs) -> list[str] | str:
        """GET HTTP Method for protocol to retrieve a list of URL."""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    async def post(
        self, urls: list[pydantic.AnyUrl], datas: list[dict], **kwargs
    ) -> list[str] | str:
        """POST HTTP Method for protocol to crawl a list of URL."""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    async def put(
        self, urls: list[pydantic.AnyUrl], datas: list[dict], **kwargs
    ) -> list[str] | str:
        """PUT HTTP Method for protocol to crawl a list of URL."""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )

    async def delete(
        self, urls: list[pydantic.AnyUrl], datas: list[dict], **kwargs
    ) -> list[str] | str:
        """DELETE HTTP Method for protocol to crawl a list of URL."""
        raise NotImplementedError(
            "Playwright engine is incldued as another lib, pip install fastcrawler[playwright]"
            "\nfrom fastcrawler_playwright import PlayWrightEngine"
        )
