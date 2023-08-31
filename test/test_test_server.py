import pytest


@pytest.mark.asyncio
async def test_test_server_response(test_server, test_requests):
    for test_request in test_requests:
        # Get the response from the test server
        test_response = await test_server.get_response(test_request.http_request)
        # Verify that the response is as expected
        for exp_attr, exp_val in test_request.expected_response_attributes.items():
            assert hasattr(test_response, exp_attr)
            assert getattr(test_response, exp_attr) == exp_val
