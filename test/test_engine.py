# pylint: skip-file
from typing import Iterable
from test.conftest import get_proxy_setting
from time import perf_counter

import pytest

from fastcrawler.engine.aio import AioHttpEngine, Morsel
from fastcrawler.engine.contracts import Request, SetCookieParam, HTTPMethod


@pytest.mark.asyncio
async def test_not_setuped_aiohttp():
    engine = AioHttpEngine(cookies=None)
    res = await engine.batch([Request(url="http://127.0.0.1:8000/get", method=HTTPMethod.GET)])
    assert engine.session is None
    await engine.teardown()
    assert type(res) is dict
    assert res["http://127.0.0.1:8000/get"] is None


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
async def test_aiohttp_proxy(user_agent):
    urls = [Request(url="https://api.ipify.org?format=json", method=HTTPMethod.GET)]
    response = None
    proxy = get_proxy_setting()
    engine = AioHttpEngine(user_agent=user_agent, proxy=proxy)
    async with engine:
        responses = (await engine.batch(urls)).values()
    for response in responses:
        assert isinstance(response.response.text, str)
    assert response is not None
    assert proxy.server in response.response.text


@pytest.mark.asyncio
async def test_aiohttp_get_request(user_agent, cookies):
    urls = [
        "http://127.0.0.1:8000/get",
        "http://127.0.0.1:8000/headers",
        "http://127.0.0.1:8000/cookies",
    ]
    async with AioHttpEngine(user_agent=user_agent, cookies=cookies) as engine:
        responses = await engine.batch(Request(url=url, method=HTTPMethod.GET) for url in urls)
    for response in responses.values():
        assert isinstance(response.response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_get_wo_user_agent_and_cookies_request():
    urls = [
        "http://127.0.0.1:8000/get",
    ]
    async with AioHttpEngine() as engine:
        responses = await engine.batch(Request(url=url, method=HTTPMethod.GET) for url in urls)
    for response in responses.values():
        assert isinstance(response.response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_post_request(aiohttp_engine: AioHttpEngine):
    urls = ["http://127.0.0.1:8000/post"]
    datas = [{"key1": "value1", "key2": "value2"}, {"key3": "value3", "key4": "value4"}]
    responses = await aiohttp_engine.batch(
        Request(url=url, data=data, method=HTTPMethod.POST) for url, data in zip(urls, datas)
    )
    for response in responses.values():
        assert isinstance(response.response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_put_request(aiohttp_engine: AioHttpEngine):
    urls = ["http://127.0.0.1:8000/put"]
    datas = [{"key1": "value1", "key2": "value2"}, {"key3": "value3", "key4": "value4"}]
    responses = await aiohttp_engine.batch(
        Request(url=url, data=data, method=HTTPMethod.PUT) for url, data in zip(urls, datas)
    )
    for response in responses.values():
        assert isinstance(response.response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_delete_request(aiohttp_engine: AioHttpEngine):
    urls = ["http://127.0.0.1:8000/delete"]
    datas = [{"key1": "value1", "key2": "value2"}, {"key3": "value3", "key4": "value4"}]
    responses = await aiohttp_engine.batch(
        Request(url=url, data=data, method=HTTPMethod.DELETE) for url, data in zip(urls, datas)
    )
    for response in responses.values():
        assert isinstance(response.response.text, str)


@pytest.mark.asyncio
async def test_aiohttp_headers(headers, user_agent):
    expected_headers = {**headers, "User-Agent": user_agent}
    async with AioHttpEngine(headers=headers, user_agent=user_agent) as aiohttp_engine:
        urls = [
            "http://127.0.0.1:8000/headers/",
        ]
        await aiohttp_engine.batch(Request(url=url, method=HTTPMethod.GET) for url in urls)
        engine_headers = aiohttp_engine.session.headers
    assert engine_headers == expected_headers == aiohttp_engine.headers


def get_morsel(cookie: SetCookieParam):
    morsel_cookie: Morsel = Morsel()
    morsel_cookie.set(cookie.name, cookie.value, cookie.value)
    return morsel_cookie


@pytest.mark.asyncio
async def test_aiohttp_cookie(cookies: Iterable[SetCookieParam], user_agent):
    cookies_origin = {cookie.name: get_morsel(cookie) for cookie in cookies}

    async with AioHttpEngine(cookies=cookies, user_agent=user_agent) as aiohttp_engine:
        urls = [
            "http://127.0.0.1:8000/cookies/",
        ]
        await aiohttp_engine.batch(Request(url=url, method=HTTPMethod.GET) for url in urls)
        assert aiohttp_engine.session
        cookies = aiohttp_engine.session.cookie_jar.filter_cookies(
            str(aiohttp_engine.session._base_url),
        )
    assert cookies_origin == cookies


@pytest.mark.asyncio
async def test_limit(headers, user_agent):
    """only test limit per host for AioHTTP engine (V Test)"""

    async with AioHttpEngine(
        headers=headers,
        user_agent=user_agent,
        connection_limit=2,
    ) as aiohttp_engine:
        urls = [
            Request(
                url="http://127.0.0.1:8000/throttled/",
                data={"seconds": 0.1},
                method=HTTPMethod.POST,
            )
            for _ in range(3)
        ]
        start = perf_counter()
        await aiohttp_engine.batch(urls)
        end = perf_counter()
    assert end - start == pytest.approx(0.2, abs=0.1)


async def test_async_event_loop(headers, user_agent):
    """Test that request are being sent in parallel (V Test)
    This test only pass if the engine is using the same event loop as the caller, and
    then the requests are being sent in parallel, so if one url is done, the next one
    is start to be processed."""

    async with AioHttpEngine(
        headers=headers,
        user_agent=user_agent,
        connection_limit=2,
    ) as aiohttp_engine:
        urls = [
            Request(
                url="http://127.0.0.1:8000/throttled",
                data={"seconds": 0.01},
                method=HTTPMethod.GET,
            ),
            Request(
                url="http://127.0.0.1:8000/throttled",
                data={"seconds": 0.3},
                method=HTTPMethod.GET,
            ),
            Request(
                url="http://127.0.0.1:8000/throttled",
                data={"seconds": 0.2},
                method=HTTPMethod.GET,
            ),
        ]
        start = perf_counter()
        await aiohttp_engine.batch(urls)
        end = perf_counter()

    assert end - start == pytest.approx(0.1, abs=0.06)
