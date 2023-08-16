import json

import websocket


def publish_data(
    image_name, operation, uuid, requestor_id, request_id, containers
):
    ws = websocket.WebSocketApp(
        "ws://localhost:3000/ws",
        on_open=on_open,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()  # Remove dispatcher parameter as it's not necessary anymore
    if operation != "list_containers":
        publish_normal_operation_on_dht(
            image_name, operation, uuid, requestor_id, request_id, ws
        )

    elif operation == "list_containers":
        publish_containers_list_on_dht(
            image_name,
            operation,
            uuid,
            requestor_id,
            request_id,
            containers,
            ws,
        )


def publish_normal_operation_on_dht(
    image_name, operation, uuid, requestor_id, request_id, ws
):
    ws_req = {
        "RequestPostTopicUUID": {
            "topic_name": "SIFIS:application_manager_" + operation,
            "topic_uuid": "application_manager_" + uuid,
            "value": {
                "operation": operation,
                "requestor_id": str(requestor_id),
                "request_id": str(request_id),
                "target": image_name,
                "result": "Successfull",
            },
        }
    }
    ws.send(json.dumps(ws_req))


def publish_containers_list_on_dht(
    image_name, operation, uuid, requestor_id, request_id, containers, ws
):
    ws_req = {
        "RequestPostTopicUUID": {
            "topic_name": "SIFIS:application_manager_" + operation,
            "topic_uuid": "application_manager_" + uuid,
            "value": {
                "operation": operation,
                "requestor_id": str(requestor_id),
                "request_id": str(request_id),
                "target": image_name,
                "result": "Successfull",
                "list": containers,
            },
        }
    }
    ws.send(json.dumps(ws_req))

    # Start the websocket connection


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")


def on_open(ws):
    print("### Connection established ###")


def send_data(
    image_name, operation, uuid, requestor_id, request_id, containers
):
    # Start a new thread to publish the data
    publish_data(
        image_name, operation, uuid, requestor_id, request_id, containers
    )
    return "Data Sent"
