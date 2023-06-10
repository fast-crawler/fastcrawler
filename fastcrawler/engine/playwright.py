import typing

import pydantic
from playwright.async_api import ProxySettings, async_playwright

from fastcrawler.engine.proto import EngineProto, ProxySetting


class Playwright(EngineProto):

    def __init__(
        self,
        headless: bool = True,
        proxy: ProxySetting = None,
        cookies: typing.List[dict] = None,
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
            await self.context.add_cookies(self.cookies)
        self.page = await self.context.new_page()
        await self.page.bring_to_front()
        return None

    async def base(self, url: pydantic.AnyUrl, method) -> str:
        """
        Base method to execute different HTTP methods for crawling purpose
        """
        await getattr(self.page, method)(url)
        return await self.page.content()

    async def get(self, urls: typing.List[pydantic.AnyUrl]):
        """
        Although Playwright is async, but URL must be retrieved in sync if one browser is being used
        """
        results = []
        for url in urls:
            result = await self.base(url, "goto")
            results.append(result)
        return results

    async def post(self):
        raise NotImplementedError(
            "This method is not implemented yet for playwright engine."
        )

    async def put(self):
        raise NotImplementedError(
            "This method is not implemented yet for playwright engine."
        )

    async def delete(self):
        raise NotImplementedError(
            "This method is not implemented yet for playwright engine."
        )

    async def teardown(self) -> None:
        """
        close the playwright browser and async manager
        """
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
