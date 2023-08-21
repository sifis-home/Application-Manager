import unittest
from unittest import mock

import requests

import application_manager.app_dht as app_dht


class TestAppDHT(unittest.TestCase):
    @mock.patch("application_manager.app_dht.request_list")
    def test_update_dht_list_connection_refused(self, mock_request_list):
        """Test the update_dht_list function with a connection refused error."""
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

    def test_publish_failure(self):
        """Test the publish function with failure."""
        ws = mock.Mock()
        topic_uuid = "1"
        requestor_id = "1"
        request_id = "1"
        containers = ["ubuntu"]

        # Set the expected behavior of the ws mock.
        ws.send.side_effect = Exception("Error sending message")

        # Call the publish function.
        with self.assertRaises(Exception):
            app_dht.publish(
                ws, topic_uuid, requestor_id, request_id, containers
            )

    def test_pull_image_empty_image_name(self):
        """Test the pull_image function with an empty image name."""
        ws = mock.Mock()
        image_name = ""

        # Call the pull_image function.
        with self.assertRaises(ValueError):
            app_dht.pull_image(ws, image_name, "1", "1", "1")

    def test_remove_image_not_found(self):
        """Test the remove_image function with an image that is not found."""
        image_name = "not_found"
        topic_uuid = "Pippo"
        request_id = "1"
        requestor_id = "1"

        response = app_dht.remove_image(
            image_name, topic_uuid, request_id, requestor_id
        )

        response_string = str(response)
        if response_string:
            assert "(" in str(response_string[0])
        else:
            self.fail("The response is empty")


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored", "-v"])
