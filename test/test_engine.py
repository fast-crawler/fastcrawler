# pylint: skip-file
from test.conftest import get_proxy_setting
from time import perf_counter

import pytest

from fastcrawler.engine.aio import AioHttpEngine, Morsel
from fastcrawler.engine.contracts import Request


@pytest.mark.asyncio
async def test_not_setuped_aiohttp():
    engine = AioHttpEngine(cookies=None)
    res = await engine.get([Request(url="http://127.0.0.1:8000/get")])
    assert engine.session is None
    await engine.teardown()
    assert res == [None]


@pytest.mark.asyncio
async def test_aiohttp_cookies_and_proxy_attr(cookies):
    proxy = get_proxy_setting()
    # None cookies
    async with AioHttpEngine(cookies=None) as engine:
        assert engine.cookies is None
    # with cookies
    async with AioHttpEngine(cookies=cookies, proxy=proxy) as engine:
        assert engine.cookies == cookies
        assert engine.proxy == proxy


@pytest.mark.asyncio
async def test_aiohttp_with_statement(user_agent):
    urls = [Request(url="http://127.0.0.1:8000/throtlled/3/")] * 10
    useragent = user_agent
    async with AioHttpEngine(useragent=useragent, connection_limit=5) as engine:
        responses = await engine.get(urls)
    for response in responses:
        assert isinstance(response.text, str)
    assert len(responses) == len(urls)


@pytest.mark.asyncio
async def test_aiohttp_proxy(user_agent):
    urls = [Request(url="https://api.ipify.org?format=json")]
    response = None
    useragent = user_agent
    proxy = get_proxy_setting()
    engine = AioHttpEngine(useragent=useragent, proxy=proxy)
    async with engine:
        responses = await engine.get(urls)
    for response in responses:
        assert isinstance(response.text, str)
    assert response is not None
    assert proxy.server in response.text


@pytest.mark.asyncio
async def test_aiohttp_get_request(user_agent, cookies):
    urls = [
        "http://127.0.0.1:8000/get",
        "http://127.0.0.1:8000/headers",
        "http://127.0.0.1:8000/cookies",
    ]
    async with AioHttpEngine(useragent=user_agent, cookies=cookies) as engine:
        responses = await engine.get(Request(url=url) for url in urls)
    for response in responses:
        assert isinstance(response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_get_wo_useragent_and_cookies_request():
    urls = [
        "http://127.0.0.1:8000/get",
    ]
    async with AioHttpEngine() as engine:
        responses = await engine.get(Request(url=url) for url in urls)
    for response in responses:
        assert isinstance(response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_post_request(aiohttp_engine: AioHttpEngine):
    urls = ["http://127.0.0.1:8000/post"]
    datas = [{"key1": "value1", "key2": "value2"}, {"key3": "value3", "key4": "value4"}]
    responses = await aiohttp_engine.post(
        Request(url=url, data=data) for url, data in zip(urls, datas)
    )
    for response in responses:
        assert isinstance(response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_put_request(aiohttp_engine: AioHttpEngine):
    urls = ["http://127.0.0.1:8000/put"]
    datas = [{"key1": "value1", "key2": "value2"}, {"key3": "value3", "key4": "value4"}]
    responses = await aiohttp_engine.put(
        Request(url=url, data=data) for url, data in zip(urls, datas)
    )
    for response in responses:
        assert isinstance(response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_delete_request(aiohttp_engine: AioHttpEngine):
    urls = ["http://127.0.0.1:8000/delete"]
    datas = [{"key1": "value1", "key2": "value2"}, {"key3": "value3", "key4": "value4"}]
    responses = await aiohttp_engine.delete(
        Request(url=url, data=data) for url, data in zip(urls, datas)
    )
    for response in responses:
        assert isinstance(response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_headers(headers, user_agent):
    expected_headers = {**headers, "User-Agent": user_agent}
    async with AioHttpEngine(headers=headers, useragent=user_agent) as aiohttp_engine:
        urls = [
            "http://127.0.0.1:8000/headers/",
        ]
        await aiohttp_engine.get(Request(url=url) for url in urls)
        engine_headers = aiohttp_engine.session.headers
    assert engine_headers == expected_headers == aiohttp_engine.headers


def get_morsel(cookie):
    morsel_cookie = Morsel()
    morsel_cookie.set(cookie.name, cookie.value, cookie.value)
    return morsel_cookie


@pytest.mark.asyncio
async def test_aiohttp_cookie(cookies, user_agent):
    cookies_origin = {cookie.name: get_morsel(cookie) for cookie in cookies}

    async with AioHttpEngine(cookies=cookies, useragent=user_agent) as aiohttp_engine:
        urls = [
            "http://127.0.0.1:8000/cookies/",
        ]
        await aiohttp_engine.get(Request(url=url) for url in urls)
        cookies = aiohttp_engine.session.cookie_jar.filter_cookies(
            str(aiohttp_engine.session._base_url),
        )
    assert cookies_origin == cookies


@pytest.mark.asyncio
async def test_limit_per_host(headers, user_agent):
    """only test limit per host for AioHTTP engine (V Test)"""

    async with AioHttpEngine(
        headers=headers,
        useragent=user_agent,
        connection_limit=3,
    ) as aiohttp_engine:
        urls_1 = [Request(url=url) for url in (["http://127.0.0.1:8000/throtlled/3/"] * 2)]
        urls_2 = [Request(url=url) for url in (["http://127.0.0.1:8000/throtlled/5/"] * 1)]
        start = perf_counter()
        await aiohttp_engine.get(urls_1 + urls_2 + urls_1)
        end = perf_counter()

    assert end - start == pytest.approx(6, abs=1)
