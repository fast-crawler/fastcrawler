import pytest
from shared.engine import get_cookies, get_proxy_setting
from shared.mock_html import get_corrupted_html, get_html
from shared.mock_json import get_json_data


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
def cookies():
    return get_cookies()
