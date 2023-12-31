import json

import rel
import websocket


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")


def on_open(ws):
    print("### Connection established ###")


def publish():
    ws = websocket.WebSocketApp(
        "ws://localhost:3000/ws",
        on_open=on_open,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt

    ws_req = {
        "RequestPostTopicUUID": {
            "topic_name": "SIFIS:app_manager",
            "topic_uuid": "application_manager_uuid",
            "value": {
                "operation": "list_containers",
                "requestor_id": "1",
                "request_id": "1",
            },
        }
    }
    ws.send(json.dumps(ws_req))


publish()
