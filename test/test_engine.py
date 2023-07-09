import pytest
from time import perf_counter

from fastcrawler.engine.aio import AioHTTP, Morsel
from test.conftest import get_proxy_setting


@pytest.mark.asyncio
async def test_aiohttp_with_statement(user_agent):
    urls = ["http://127.0.0.1:8000/throtlled/3/"] * 10
    useragent = user_agent
    async with AioHTTP(useragent=useragent, connection_limit=5) as engine:
        responses = await engine.get(urls)
    for response in responses:
        assert isinstance(response, str)
    assert len(responses) == len(urls)


@pytest.mark.asyncio
async def test_aiohttp_proxy(user_agent):
    urls = ["https://api.ipify.org?format=json"]
    useragent = user_agent
    proxy = get_proxy_setting()
    engine = AioHTTP(useragent=useragent, proxy=proxy)
    async with engine:
        responses = await engine.get(urls)
    for response in responses:
        assert isinstance(response, str)
    assert proxy.server in response


@pytest.mark.asyncio
async def test_aiohttp_get_request(user_agent, cookies):
    urls = [
        "http://127.0.0.1:8000/get",
        "http://127.0.0.1:8000/headers",
        "http://127.0.0.1:8000/cookies",
    ]
    async with AioHTTP(useragent=user_agent, cookies=cookies) as engine:
        responses = await engine.get(urls)
    for response in responses:
        assert isinstance(response, str)

@pytest.mark.asyncio
async def test_aiohttp_get_wo_useragent_and_cookies_request():
    urls = [
        "http://127.0.0.1:8000/get",
    ]
    async with AioHTTP() as engine:
        responses = await engine.get(urls)
    for response in responses:
        assert isinstance(response, str)


@pytest.mark.asyncio
async def test_aiohttp_post_request(aiohttp_engine):
    urls = ["http://127.0.0.1:8000/post"]
    datas = [{"key1": "value1", "key2": "value2"}, {"key3": "value3", "key4": "value4"}]
    responses = await aiohttp_engine.post(urls, datas)
    for response in responses:
        assert isinstance(response, str)


@pytest.mark.asyncio
async def test_aiohttp_put_request(aiohttp_engine):
    urls = ["http://127.0.0.1:8000/put"]
    datas = [{"key1": "value1", "key2": "value2"}, {"key3": "value3", "key4": "value4"}]
    responses = await aiohttp_engine.put(urls, datas)
    for response in responses:
        assert isinstance(response, str)


@pytest.mark.asyncio
async def test_aiohttp_delete_request(aiohttp_engine):
    urls = ["http://127.0.0.1:8000/delete"]
    datas = [{"key1": "value1", "key2": "value2"}, {"key3": "value3", "key4": "value4"}]
    responses = await aiohttp_engine.delete(urls, datas)
    for response in responses:
        assert isinstance(response, str)


@pytest.mark.asyncio
async def test_aiohttp_headers(headers, user_agent):
    expected_headers = {**headers, "User-Agent": user_agent}
    async with AioHTTP(headers=headers, useragent=user_agent) as aiohttp_engine:
        urls = [
            "http://127.0.0.1:8000/headers/",
        ]
        responses = await aiohttp_engine.get(urls)
        engine_headers = aiohttp_engine.session.headers
    assert engine_headers == expected_headers == aiohttp_engine.headers


def get_morsel(cookie):
    morsel_cookie = Morsel()
    morsel_cookie.set(cookie.name, cookie.value, cookie.value)
    return morsel_cookie


@pytest.mark.asyncio
async def test_aiohttp_cookie(cookies, user_agent):
    cookies_origin = {cookie.name: get_morsel(cookie) for cookie in cookies}

    async with AioHTTP(cookies=cookies, useragent=user_agent) as aiohttp_engine:
        urls = [
            "http://127.0.0.1:8000/cookies/",
        ]
        responses = await aiohttp_engine.get(urls)
        cookies = aiohttp_engine.session.cookie_jar.filter_cookies(str(aiohttp_engine.session._base_url))
    assert cookies_origin == cookies


@pytest.mark.asyncio
async def test_limit_per_host(headers, user_agent):
    """only test limit per host for AioHTTP engine (V Test)"""

    async with AioHTTP(headers=headers, useragent=user_agent, connection_limit=5) as aiohttp_engine:
        urls_1 = ["http://127.0.0.1:8000/throtlled/5/"] * 4
        urls_2 = ["http://127.0.0.1:8000/throtlled/10/"] * 4
        t0 = perf_counter()
        await aiohttp_engine.get(urls_1 + urls_2 + urls_1)
        t1 = perf_counter()

    assert t1 - t0 == pytest.approx(20, abs=1)
