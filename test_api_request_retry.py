import unittest
from unittest.mock import patch

import requests

import api


class DummyResponse:
    def __init__(self, status_code=200, text="ok"):
        self.status_code = status_code
        self.text = text


class RequestRetryTests(unittest.TestCase):
    def test_retries_after_timeout_then_succeeds(self):
        success = DummyResponse(status_code=200)

        with patch(
            "api.requests.get",
            side_effect=[requests.exceptions.Timeout(), success],
        ) as mock_get, patch("api.time.sleep"):
            response = api.request_get_with_retry(
                "http://example.com",
                params={"pageNo": 1},
                timeout=5,
                attempts=2,
                retry_delay=0,
            )

        self.assertIs(response, success)
        self.assertEqual(mock_get.call_count, 2)

    def test_returns_none_after_repeated_non_200(self):
        with patch(
            "api.requests.get",
            side_effect=[DummyResponse(status_code=500), DummyResponse(status_code=503)],
        ) as mock_get, patch("api.time.sleep"):
            response = api.request_get_with_retry(
                "http://example.com",
                params={"pageNo": 1},
                timeout=5,
                attempts=2,
                retry_delay=0,
            )

        self.assertIsNone(response)
        self.assertEqual(mock_get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
