# pylint: skip-file

from fastcrawler import Logger
from test.shared.engine import (
    get_aiohttp_engine,
    get_cookies,
    get_headers,
    get_proxy_setting,
    get_random_useragent,
)
from test.shared.mock_html import get_corrupted_html, get_html
from test.shared.mock_json import get_json_data

import pytest
import pytest_asyncio

from fastcrawler.schedule.adopter import RocketryApplication, RocketryController


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


@pytest_asyncio.fixture()
async def aiohttp_engine():
    setuped_engine = await get_aiohttp_engine()
    yield setuped_engine
    await setuped_engine.teardown()


@pytest.fixture(scope="function")
def task_app():
    yield RocketryApplication()


@pytest.fixture(scope="function")
def task_manager(task_app):
    yield RocketryController(task_app)


@pytest.fixture(scope="function")
def logger():
    return Logger()
