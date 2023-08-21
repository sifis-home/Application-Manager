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

        # Set up a mock response for requests.get to simulate Connection Refused error
        mock_response = mock.Mock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.ConnectionError("Connection refused")
        )
        mock_request_list.get.return_value = mock_response

        # Test the function with the mock setup
        with self.assertRaises(requests.exceptions.ConnectionError):
            app_dht.update_dht_list(mock_ws, mock_message)

    def pull_image(ws, image_name, topic_uuid, requestor_id, request_id):
        """Pull an image from the DHT.

        Args:
            ws: The websocket object.
            image_name: The name of the image to pull.
            topic_uuid: The UUID of the topic.
            requestor_id: The ID of the requestor.
            request_id: The ID of the request.

        Returns:
            A string representing the status of the pull operation.
        """
        # Try to get the response from the server
        try:
            response = requests.get(api_url + "topic_name/" + topic_name)
        except requests.exceptions.ConnectionError:
            # If the connection fails, return an error
            raise ConnectionError()

        # If the response is successful, return the image name
        if response.status_code == 200:
            return image_name

        # If the response is not successful, return an error
        return "Error"

    def test_pull_image_success(self):
        """Test the pull_image function with success."""
        image_name = "ubuntu"
        result, status_code = app_dht.pull_image(
            image_name, None, None, None, None
        )
        assert result == f"Missing 'image_name' parameter"
        assert status_code == 400


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored", "-v"])
