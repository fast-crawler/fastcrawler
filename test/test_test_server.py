import pytest

from fastcrawler.test_utils import TestServer, MockEngine
from test.shared.test_server import routes, test_requests as __test_requests, BASE_URL


@pytest.fixture(scope="session")
def test_server():
    yield TestServer(routes=routes)


@pytest.fixture(scope="session")
def test_requests():
    yield __test_requests


@pytest.fixture(scope="session")
def mock_engine(test_server):
    yield MockEngine(test_server, BASE_URL)


# @pytest.mark.asyncio
# async def test_test_server_response(test_server, test_requests):
#     for test_request in test_requests:
#         # Get the response from the test server
#         test_response = await test_server.get_response(test_request.http_request)
#         # Verify that the response is as expected
#         for exp_attr, exp_val in test_request.expected_response_attributes.items():
#             assert hasattr(test_response, exp_attr)
#             assert getattr(test_response, exp_attr) == exp_val


@pytest.mark.asyncio
async def test_base_mock_engine(mock_engine: MockEngine, test_requests):
    for test_request in test_requests:
        # Get the response from the test server
        test_response = await mock_engine.base(test_request.http_request)
        # Verify that the response is as expected
        for exp_attr, exp_val in test_request.expected_response_attributes.items():
            assert hasattr(test_response, exp_attr)
            assert getattr(test_response, exp_attr) == exp_val


@pytest.mark.asyncio
async def test_batch_mock_engine(mock_engine: MockEngine, test_requests):
    # Get the response from the test server
    url_test_response_dct = await mock_engine.batch(
        [test_request.http_request for test_request in test_requests]
    )
    # Verify that the response is as expected
    for test_request in test_requests:
        test_response = url_test_response_dct[test_request.http_request.url]
        for exp_attr, exp_val in test_request.expected_response_attributes.items():
            assert hasattr(test_response, exp_attr)
            assert getattr(test_response, exp_attr) == exp_val
