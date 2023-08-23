import json

import app_dht
import security_by_contract
import websocket


def handle_pull_image(ws, topic_name, topic_uuid):
    try:
        image_name = topic_name["image_name"]
        security_by_contract.get_labels(image_name)

        requestor_id = topic_name["requestor_id"]
        request_id = topic_name["request_id"]
        result = app_dht.pull_image(
            ws, image_name, topic_uuid, requestor_id, request_id
        )
        print(result)
    except Exception as e:
        print(e)


def handle_start_container(topic_name):
    try:
        image_name = topic_name["image_name"]
        result = app_dht.start_container(image_name)
        print(result)
    except Exception as e:
        print(e)


def handle_remove_image(topic_name, topic_uuid):
    try:
        image_name = topic_name["image_name"]
        request_id = topic_name["request_id"]
        requestor_id = topic_name["requestor_id"]
        result = app_dht.remove_image(
            image_name, topic_uuid, request_id, requestor_id
        )
        print(result)
    except Exception as e:
        print(e)


def handle_stop_container(topic_name, topic_uuid):
    try:
        container_id = topic_name["container_id"]
        request_id = topic_name["request_id"]
        requestor_id = topic_name["requestor_id"]
        result = app_dht.stop_container(
            container_id, topic_uuid, request_id, requestor_id
        )
        print(result)
    except Exception as e:
        print(e)


def handle_remove_container(topic_name):
    try:
        container_id = topic_name["container_id"]
        result = app_dht.remove_container(container_id)
        print(result)
    except Exception as e:
        print(e)


def handle_list_containers(topic_uuid, requestor_id, request_id):
    try:
        result = app_dht.list_containers(
            topic_uuid, requestor_id, request_id, None
        )
        print(result)
    except Exception as e:
        print(e)


def on_message(ws, message):
    json_message = json.loads(message)

    if "Persistent" in json_message:
        json_message = json_message["Persistent"]
        # Handle messages
        topic_name = json_message["topic_name"]
        topic_uuid = json_message["topic_uuid"]
        if topic_name == "SIFIS:app_manager":
            if "value" in json_message:
                topic_value = json_message["value"]
                request_id = topic_value["request_id"]
                requestor_id = topic_value["requestor_id"]
                handle_message(
                    ws, topic_uuid, topic_value, request_id, requestor_id
                )


def handle_message(ws, topic_uuid, topic_value, request_id, requestor_id):
    if "operation" in topic_value:
        operation = topic_value["operation"]
        if operation == "pull_image":
            handle_pull_image(ws, topic_value, topic_uuid)
        elif operation == "remove_image":
            handle_remove_image(topic_value, topic_uuid)
        elif operation == "start_container":
            handle_start_container(topic_value)
        elif operation == "stop_container":
            handle_stop_container(topic_value, topic_uuid)
        elif operation == "remove_container":
            handle_remove_container(topic_value)
        elif operation == "list_containers":
            handle_list_containers(topic_uuid, requestor_id, request_id)


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
