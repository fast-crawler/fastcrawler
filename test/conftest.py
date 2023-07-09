# pylint: skip-file
import asyncio

import pytest

from test.shared.engine import (
    get_cookies,
    get_random_useragent,
    get_proxy_setting,
    get_aiohttp_engine,
    get_headers,
)
from test.shared.mock_html import get_corrupted_html, get_html
from test.shared.mock_json import get_json_data


@pytest.fixture
def html():
    return get_html()


@pytest.fixture
def corrupted_html():
    return get_corrupted_html()


@pytest.fixture
def json_data():
    return get_json_data()


@pytest.fixture
def proxy_setting():
    return get_proxy_setting()


@pytest.fixture
def user_agent():
    return get_random_useragent()


@pytest.fixture
def headers():
    return get_headers()


@pytest.fixture
def cookies():
    return get_cookies()


@pytest.fixture()
def aiohttp_engine():
    engine = get_aiohttp_engine()
    yield engine
    asyncio.run(engine.teardown())
