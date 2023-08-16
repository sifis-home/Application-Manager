import json
import unittest.mock
from io import StringIO
from unittest.mock import patch

import pytest

import app_dht
import catch_topic


def test_handle_pull_image():
    topic_name = {"image_name": "my_image"}
    expected_output = "Image pulled successfully."
    with patch("app_dht.pull_image", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_pull_image(
                topic_name,
                uuid="my_uuid",
                requestor_id="my_requestor_id",
                request_id="my_request_id",
            )
            output = fake_output.getvalue().strip()
            assert output == expected_output


def test_handle_start_container():
    topic_name = {"image_name": "my_image"}
    expected_output = "Container started successfully."
    with patch("app_dht.start_container", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_start_container(
                topic_name,
                uuid="my_uuid",
                requestor_id="my_requestor_id",
                request_id="my_request_id",
            )
            output = fake_output.getvalue().strip()
            assert output == expected_output


def test_handle_stop_container():
    topic_name = {"container_id": "my_container"}
    expected_output = "Container stopped successfully."
    with patch("app_dht.stop_container", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_stop_container(
                topic_name,
                uuid="my_uuid",
                requestor_id="my_requestor_id",
                request_id="my_request_id",
            )
            output = fake_output.getvalue().strip()
            assert output == expected_output


@patch("json.loads")
def test_on_message_start_container(mock_loads):
    mock_message = json.dumps(
        {
            "Persistent": {
                "topic_name": "SIFIS:app_manager",
                "value": {
                    "operation": "start_container",
                    "image_name": "my_image",
                },
            }
        }
    )
    mock_loads.return_value = json.loads(mock_message)
    with patch("app_dht.start_container"):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            ws = catch_topic.websocket.WebSocketApp("ws://localhost:3000/ws")
            catch_topic.on_message(ws, mock_message)
            output = fake_output.getvalue().strip()
            assert "Received:" in output


def test_handle_remove_container():
    topic_name = {"container_id": "my_container"}
    expected_output = "Container removed successfully."
    with patch("app_dht.remove_container", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_remove_container(
                topic_name,
                uuid="my_uuid",
                requestor_id="my_requestor_id",
                request_id="my_request_id",
            )
            output = fake_output.getvalue().strip()
            assert output == expected_output


@patch("json.loads")
def test_on_message_pull_image(mock_loads):
    mock_message = json.dumps(
        {
            "Persistent": {
                "topic_name": "SIFIS:app_manager",
                "value": {"operation": "pull_image", "image_name": "my_image"},
            }
        }
    )
    mock_loads.return_value = json.loads(mock_message)
    with patch("app_dht.pull_image"):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            ws = catch_topic.websocket.WebSocketApp("ws://localhost:3000/ws")
            catch_topic.on_message(ws, mock_message)
            output = fake_output.getvalue().strip()
            assert "Received:" in output


def test_handle_remove_image():
    topic_name = {"image_name": "my_image"}
    expected_output = "Image removed successfully."
    with patch("app_dht.remove_image", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_remove_image(
                topic_name,
                uuid="my_uuid",
                requestor_id="my_requestor_id",
                request_id="my_request_id",
            )
            output = fake_output.getvalue().strip()
            assert output == expected_output


# Add more test functions for other functions...


@patch("json.loads")
def test_on_message_remove_image(mock_loads):
    mock_message = json.dumps(
        {
            "Persistent": {
                "topic_name": "SIFIS:app_manager",
                "value": {
                    "operation": "remove_image",
                    "image_name": "my_image",
                },
            }
        }
    )
    mock_loads.return_value = json.loads(mock_message)
    with patch("app_dht.remove_image"):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            ws = catch_topic.websocket.WebSocketApp("ws://localhost:3000/ws")
            catch_topic.on_message(ws, mock_message)
            output = fake_output.getvalue().strip()
            assert "Received:" in output


def test_handle_list_containers():
    expected_output = "List of containers: container1, container2, container3"
    with patch("app_dht.list_containers", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_list_containers(
                uuid="my_uuid",
                requestor_id="my_requestor_id",
                request_id="my_request_id",
            )
            output = fake_output.getvalue().strip()
            assert output == expected_output


import unittest

import mock


class TestListContainers(unittest.TestCase):
    @mock.patch("app_dht.list_containers")
    def test_list_containers(self, mock_list_containers):
        mock_list_containers.return_value = [
            "container_1 (container_1)",
            "container_2 (container_2)",
        ]

        app_dht.list_containers(
            uuid="1234567890", requestor_id="1", request_id="1"
        )

        self.assertEqual(
            mock_list_containers.call_args,
            mock.call(uuid="1234567890", requestor_id="1", request_id="1"),
        )


@pytest.fixture
def mock_pull_image():
    return mock.Mock()


def test_pull_image(mock_pull_image):
    with mock.patch("app_dht.pull_image", mock_pull_image):
        mock_pull_image.return_value = "Image pulled successfully!"

        app_dht.pull_image(
            image_name="test_image",
            uuid="1234567890",
            requestor_id="1",
            request_id="1",
        )

        mock_pull_image.assert_called_once_with(
            image_name="test_image",
            uuid="1234567890",
            requestor_id="1",
            request_id="1",
        )


if __name__ == "__main__":
    pytest.main()
