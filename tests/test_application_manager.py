import unittest
from unittest import mock

import requests

import application_manager.app_dht as app_dht


class TestAppDHT(unittest.TestCase):
    @mock.patch("application_manager.app_dht.request_list")
    def test_update_dht_list_connection_refused(self, mock_request_list):
        # Mocking WebSocket object
        mock_ws = mock.Mock()

        # Mocking response message
        mock_message = '{"value": {}}'

        # Mocking image name
        mock_image_name = "test_image"

        # Set up a mock response for requests.get to simulate Connection Refused error
        mock_response = mock.Mock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.ConnectionError("Connection refused")
        )
        mock_request_list.get.return_value = mock_response

        # Test the function with the mock setup
        with self.assertRaises(requests.exceptions.ConnectionError):
            app_dht.update_dht_list(mock_ws, mock_message)


if __name__ == "__main__":
    unittest.main()
