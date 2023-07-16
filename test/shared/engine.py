# pylint: skip-file
from random import choice

from pydantic_settings import BaseSettings

from fastcrawler.engine import ProxySetting, SetCookieParam
from fastcrawler.engine.aio import AioHttpEngine

sample_cookies = [
    SetCookieParam(
        name="test_cookie",
        value="test_value",
        path="/",
    ),
    SetCookieParam(
        name="test_cookie2",
        value="test_value2",
        path="/",
    ),
]

useragents = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    ),
]


class Setting(BaseSettings):
    server: str
    port: int
    username: str
    password: str

    class Config:
        env_file = ".env"


setting = Setting()


def get_proxy_setting():
    return ProxySetting(
        protocol="http://",
        server=setting.server,
        port=setting.port,
        username=setting.username,
        password=setting.password,
    )


def get_headers():
    return {"Accept": "*/*", "Accept-Encoding": "gzip, deflate, br"}


def get_random_useragent():
    return choice(useragents)


def get_cookies():
    return sample_cookies


async def get_aiohttp_engine():
    headers = {}
    engine = AioHttpEngine(
        cookies=get_cookies(),
        headers=headers,
        useragent=get_random_useragent(),
    )
    await engine.setup()
    return engine
