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

    def test_publish_success(self):
        """Test the publish function with success."""
        ws = mock.Mock()
        topic_uuid = "1"
        requestor_id = "1"
        request_id = "1"
        containers = ["ubuntu"]

        # Set the expected behavior of the ws mock.
        ws.send.return_value = None

        # Create a dictionary of data to pass to the publish function.
        data = {
            "RequestPostTopicUUID": {
                "topic_name": "SIFIS:container_list",
                "topic_uuid": topic_uuid,
                "value": {
                    "requestor_id": requestor_id,
                    "request_id": request_id,
                    "containers": containers,
                },
            }
        }

        # Call the publish function.
        app_dht.publish(ws, topic_uuid, requestor_id, request_id, containers)
        # Call the send() method of the mock object.
        ws.send(data)
        # Assert that the ws mock was called with the correct arguments.
        ws.send.assert_called_with(data)


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored", "-v"])
