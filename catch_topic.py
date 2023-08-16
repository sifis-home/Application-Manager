import json

import websocket

import app_dht


def handle_pull_image(topic_name, uuid, requestor_id, request_id):
    try:
        image_name = topic_name["image_name"]
        result = app_dht.pull_image(image_name, uuid, requestor_id, request_id)
        print(result)
    except Exception as e:
        print(e)


def handle_start_container(topic_name, uuid, requestor_id, request_id):
    try:
        image_name = topic_name["image_name"]
        result = app_dht.start_container(
            image_name, uuid, requestor_id, request_id
        )
        print(result)
    except Exception as e:
        print(e)


def handle_remove_image(topic_name, uuid, requestor_id, request_id):
    try:
        image_name = topic_name["image_name"]
        result = app_dht.remove_image(
            image_name, uuid, requestor_id, request_id
        )
        print(result)
    except Exception as e:
        print(e)


def handle_stop_container(topic_name, uuid, requestor_id, request_id):
    try:
        container_id = topic_name["container_id"]
        result = app_dht.stop_container(
            container_id, uuid, requestor_id, request_id
        )
        print(result)
    except Exception as e:
        print(e)


def handle_remove_container(topic_name, uuid, requestor_id, request_id):
    try:
        container_id = topic_name["container_id"]
        result = app_dht.remove_container(
            container_id, uuid, requestor_id, request_id
        )
        print(result)
    except Exception as e:
        print(e)


def handle_list_containers(uuid, requestor_id, request_id):
    try:
        result = app_dht.list_containers(uuid, requestor_id, request_id)
        print(result)
    except Exception as e:
        print(e)


def on_message(ws, message):
    print("Received:")

    json_message = json.loads(message)

    if "Persistent" in json_message:
        json_message = json_message["Persistent"]

        print("JSON-MESSAGE")
        print(json_message["topic_name"])
        uuid = json_message["topic_uuid"]

        # Handle messages
        topic_name = json_message["topic_name"]
        if topic_name == "SIFIS:app_manager":
            if "value" in json_message:
                topic_value = json_message["value"]
                requestor_id = json_message["requestor_id"]
                request_id = json_message["request_id"]
                if "operation" in topic_value:
                    operation = topic_value["operation"]
                    if operation == "pull_image":
                        handle_pull_image(
                            topic_value, uuid, requestor_id, request_id
                        )
                    elif operation == "remove_image":
                        handle_remove_image(
                            topic_value, uuid, requestor_id, request_id
                        )
                    elif operation == "start_container":
                        handle_start_container(
                            topic_value, uuid, requestor_id, request_id
                        )
                    elif operation == "stop_container":
                        handle_stop_container(
                            topic_value, uuid, requestor_id, request_id
                        )
                    elif operation == "remove_container":
                        handle_remove_container(
                            topic_value, uuid, requestor_id, request_id
                        )
                    elif operation == "list_containers":
                        handle_list_containers(uuid, requestor_id, request_id)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")


def on_open(ws):
    print("### Connection established ###")


if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "ws://localhost:3000/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()
