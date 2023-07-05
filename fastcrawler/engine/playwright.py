from typing import List

import pydantic
from playwright.async_api import Browser, Page, ProxySettings, async_playwright
from playwright.async_api._context_manager import PlaywrightContextManager

from fastcrawler.engine.base import EngineProto, ProxySetting, SetCookieParam


class Playwright(EngineProto):
    """
    Playwrright is one of the engines written from the protocol, using playwright library.

    To use this engine in library, simply set as your Spider's class's attribute and you're good to go:)
    Example:

    class MySpider(Spider):
        engine = engine.Playwright


    If you wish to change the behavior of this engine, you can create your own engine adhering from
        this engine, simply subclass this class and override methods you want to change.

    By default, it uses `Mozila Firefox` browser which I assume is the best one out there,
        no CDP and etc, less overhead.

    """
    page: Page
    browser: Browser
    async_manager: PlaywrightContextManager | None

    def __init__(
        self,
        headless: bool = True,
        proxy: ProxySetting | None = None,
        cookies: List[SetCookieParam] | None = None,
        useragent: dict | None = None
    ):
        """ initilize the playwright with proxy, headless, and cookies
        """
        self.proxy = proxy
        self._proxy = None
        if proxy:
            self._proxy = ProxySettings(
                server=f"{proxy.protocol}{proxy.server}:{proxy.port}",
                username=proxy.username,
                password=proxy.password
            )
        self.headless = headless
        self.cookies = cookies
        self.useragent = useragent
        self.driver = None
        self.context = None

    async def setup(self) -> None:
        """
        setup the playwright browser
        """
        self.async_manager = async_playwright()
        self.driver = await self.async_manager.start()
        self.browser = await self.driver.firefox.launch(
            headless=self.headless,
        )
        self.context = await self.browser.new_context(
            accept_downloads=True,
            proxy=self._proxy,
        )
        if self.cookies:
            await self.context.add_cookies(self.cookies)  # type: ignore
        self.page = await self.context.new_page()
        await self.page.bring_to_front()
        return None

    async def base(self, url: pydantic.AnyUrl, method: str, data: dict | None = None) -> str:
        """
        Base method to execute different HTTP methods for crawling purpose
        """
        if not data:
            await getattr(self.page, method)(url)
        else:
            raise NotImplementedError("Passing body data is not supported in browser protocol")
        return await self.page.content()  # type: ignore

    async def get(self, urls: List[pydantic.AnyUrl]) -> list:
        """
        Although Playwright is async, but URL must be retrieved in sync if one browser is being used
        """
        results = []
        for url in urls:
            result = await self.base(url, "goto", data=None)
            results.append(result)
        return results

    async def post(self, urls: List[pydantic.AnyUrl] = ..., datas: List[dict] = ...):  # type: ignore
        raise NotImplementedError(
            "POST method is not implemented yet for playwright engine."
        )

    async def put(self, urls: List[pydantic.AnyUrl] = ..., datas: List[dict] = ...):  # type: ignore
        raise NotImplementedError(
            "PUT method is not implemented yet for playwright engine."
        )

    async def delete(self, urls: List[pydantic.AnyUrl] = ..., datas: List[dict] = ...):  # type: ignore
        raise NotImplementedError(
            "GET method is not implemented yet for playwright engine."
        )

    async def teardown(self) -> None:
        """
        close the playwright browser and async manager
        """
        if isinstance(self.async_manager, PlaywrightContextManager):
            await self.browser.close()
            await self.async_manager.__aexit__()
            self.async_manager = None
        return None

    async def __aenter__(self):
        """
        Keeps the compability with async manager
        """
        await self.setup()
        return self

    async def __aexit__(self, *_):
        """
        Keeps the compability with async manager
        """
        await self.teardown()
