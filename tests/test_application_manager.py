import json
from io import StringIO
from unittest.mock import patch

import pytest

import catch_topic


def test_handle_pull_image():
    topic_name = {"image_name": "my_image"}
    expected_output = "Image pulled successfully."
    with patch("app_dht.pull_image", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_pull_image(topic_name)
            output = fake_output.getvalue().strip()
            assert output == expected_output


def test_handle_start_container():
    topic_name = {"image_name": "my_image"}
    expected_output = "Container started successfully."
    with patch("app_dht.start_container", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_start_container(topic_name)
            output = fake_output.getvalue().strip()
            assert output == expected_output


def test_handle_stop_container():
    topic_name = {"container_id": "my_container"}
    expected_output = "Container stopped successfully."
    with patch("app_dht.stop_container", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_stop_container(topic_name)
            output = fake_output.getvalue().strip()
            assert output == expected_output


def test_handle_remove_container():
    topic_name = {"container_id": "my_container"}
    expected_output = "Container removed successfully."
    with patch("app_dht.remove_container", return_value=expected_output):
        with patch("sys.stdout", new=StringIO()) as fake_output:
            catch_topic.handle_remove_container(topic_name)
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
            catch_topic.handle_remove_image(topic_name)
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
            catch_topic.handle_list_containers()
            output = fake_output.getvalue().strip()
            assert output == expected_output


if __name__ == "__main__":
    pytest.main()
