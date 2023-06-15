# pylint: skip-file

import pytest
from playwright.async_api import Page

from fastcrawler.engine import Playwright


@pytest.mark.asyncio
async def test_setup():
    async with Playwright() as playwright_engine:
        assert isinstance(playwright_engine.page, Page)

@pytest.mark.asyncio
async def test_base_and_proxy(proxy_setting):
    url = "https://api.ipify.org/?format=json"
    async with Playwright(proxy=proxy_setting, headless=True,) as playwright_engine:
        content = await playwright_engine.base(url, "goto")
        assert playwright_engine.proxy.server in content

@pytest.mark.asyncio
async def test_get_all_no_proxy():
    urls = ["https://api.ipify.org/?format=json"] * 2
    async with Playwright(headless=True) as playwright_engine:
        contents = await playwright_engine.get(urls)
        assert all("ip" in content for content in contents)

@pytest.mark.asyncio
async def test_not_implemented_methods():
    async with Playwright() as playwright_engine:
        with pytest.raises(NotImplementedError):
            await playwright_engine.post()

        with pytest.raises(NotImplementedError):
            await playwright_engine.put()

        with pytest.raises(NotImplementedError):
            await playwright_engine.delete()

@pytest.mark.asyncio
async def test_teardown():
    async with Playwright() as playwright_engine:
        pass
    assert playwright_engine.async_manager is None


@pytest.mark.asyncio
async def test_cookies(cookies):
    async with Playwright(cookies=cookies) as playwright_engine:
        await playwright_engine.page.goto('http://example.com')
        context_cookies = await playwright_engine.context.cookies()
        context_cookies_dict = {cookie['name']: cookie['value'] for cookie in context_cookies}
        original_cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        assert context_cookies_dict == original_cookies_dict
