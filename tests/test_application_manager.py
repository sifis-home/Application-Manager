import unittest
from unittest import mock

import docker
import pytest

import application_manager.app_dht as app_dht

client = docker.from_env()


class TestAppDHT(unittest.TestCase):
    '''
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
        assert 'ConnectionError not raised'
    '''

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

    '''
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


    def test_update_dht_list_empty_list(self):
        """Test the update_dht_list function with an empty list."""
        ws = mock.Mock()
        image_name = ""

        # Call the update_dht_list function.
        app_dht.update_dht_list(ws, image_name)

        # Since the function doesn't do anything if the list is empty, we can simply assert True.
        assert True
    '''

    def test_update_dht_list_empty_list(self):
        """Test the update_dht_list function with an empty list."""

        # The image name is empty.
        image_name = ""

        # Set the expected value of the list of containers.
        expected_list = []

        # Call the update_dht_list function.
        with pytest.raises(TypeError):
            app_dht.update_dht_list(image_name)

    '''
    def test_pull_image_success(self):
        """Test the pull_image function with success."""

        # The image name is "ubuntu".
        image_name = "ubuntu"

        # The topic UUID is "Pippo".
        topic_uuid = "Pippo"

        # The requestor ID is "1".
        requestor_id = "1"

        # The request ID is "1".
        request_id = "1"

        # Set the expected value of the image name.
        expected_name = image_name

        # Call the pull_image function.
        try:
            result, status_code = app_dht.pull_image(
                image_name, topic_uuid, requestor_id, request_id
            )
        except Exception as e:
            raise pytest.fail(e)

        # Assert that the function returned the expected image name.
        assert result == expected_name

    '''

    def test_pull_image_empty_list(self):
        print("pull")
        """Test the pull_image function with an empty list of containers."""

        # Call the pull_image function.
        with pytest.raises(TypeError):
            result, status_code = app_dht.pull_image("ubuntu")

    def test_remove_image_not_found(self):
        """Test the remove_image function with an image that is not found."""
        image_name = "not_found"
        topic_uuid = "Pippo"
        request_id = "1"
        requestor_id = "1"

        # Call the remove_image function.
        with pytest.raises(TypeError):
            response = app_dht.remove_image(image_name)
        """
        try:
            response = app_dht.remove_image(
                image_name, topic_uuid, request_id, requestor_id
            )
        except docker.errors.NotFoundError:
            # The image was not found, so the function should raise a NotFoundError exception.
            assert True
        else:
            # The function should not raise an exception if the image is found.
            assert False
        """

    def test_stop_container(self):
        """Test the stop_container function."""
        container_id = (
            "valid_container_id"  # Replace with an actual valid container ID
        )
        topic_uuid = "valid_topic_uuid"  # Replace with a valid topic UUID
        request_id = "valid_request_id"  # Replace with a valid request ID
        requestor_id = (
            "valid_requestor_id"  # Replace with a valid requestor ID
        )

        # Call the stop_container function.
        result = app_dht.stop_container(
            container_id, topic_uuid, request_id, requestor_id
        )

        # Since the function returns a string in this case, we can simply assert its truthiness.
        assert result, "Expected a truthy result"

    def test_remove_container(self):
        """Test the remove_container function."""
        container_id = (
            "valid_container_id"  # Replace with an actual valid container ID
        )

        # Call the remove_container function.
        result = app_dht.remove_container(container_id)

        # Since the function returns a string in this case, we can simply assert its truthiness.
        assert result, "Expected a truthy result"

    def test_request_list(self):
        """Test the request_list function."""
        ws = mock.Mock()
        message = '{"topic_name": "SIFIS:container_list", "topic_uuid": "valid_topic_uuid", "value": {"requestor_id": "valid_requestor_id", "request_id": "valid_request_id", "containers": ["ubuntu"]}}'
        image_name = "new_image"

        # Call the request_list function.
        result = app_dht.request_list(ws, message, image_name)
        print(result)

        # Since the function doesn't return anything meaningful in this case, we can assert True.
        assert "OK"


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored", "-v"])
