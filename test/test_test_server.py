import pytest


@pytest.mark.asyncio
async def test_test_server_response(test_server, test_requests):
    for test_request in test_requests:
        # Get the response from the test server
        test_response = await test_server.get_response(test_request.request)
        # Verify that the response is as expected
        for attr, val in test_request.attrs.items():
            assert getattr(test_response, attr) == val
