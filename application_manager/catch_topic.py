import json

import app_dht
import requests
import security_by_contract
import websocket

REGISTERED = False
registration_id = 1
session_id = "None"
permit_installation = False


def UCS_request(ws, topic_name, topic_uuid, request_id, requestor_id):
    global REGISTERED, session_id
    try:
        image_name = topic_name["image_name"]
        image_name = image_name.replace("ghcr.io/sifis-home/", "").replace(":latest", "")
        print("[!] Recovering App LABELS\n")
        _, app_id = security_by_contract.get_labels(image_name)
        session_id = app_id
        if session_id == "None":
            notify_mobile_application(
                image_name, topic_uuid, request_id, requestor_id
            )
        else:
            print("[!] APP_ID: " + str(session_id))
            return
    except Exception as e:
        print(e)


def notify_mobile_application(
    image_name, topic_uuid, request_id, requestor_id
):
    topic_name = "SIFIS:notification_message"
    print("[!] " + notification)
    notification = (
        "The "
        + image_name
        + " cannot be installed, the operation is NOT permitted by Usage Control"
    )
    address = "http://146.48.89.28:3000/"
    notification_data = {
        "requestor_id": requestor_id,
        "request_id": request_id,
        "message": notification,
    }
    requests.post(
        address + "topic_name/" + topic_name + "/topic_uuid/" + topic_uuid,
        json=notification_data,
    )
    return


def handle_pull_image():
    global REGISTERED, session_id, global_pull_image_params

    # Accedi ai parametri globali
    params = global_pull_image_params
    if params is not None:
        ws = params["ws"]
        topic_value = params["topic_value"]
        topic_uuid = params["topic_uuid"]
        try:
            image_name = topic_value["image_name"]
            try:
                image_name = image_name.replace("ghcr.io/sifis-home/", "").replace(":latest", "")
            except:
                pass
            requestor_id = topic_value["requestor_id"]
            request_id = topic_value["request_id"]
            result = app_dht.pull_image(
                ws, image_name, topic_uuid, requestor_id, request_id
            )
            print(result)
            print(
                "\n-----------------  PULLING OPERATION COMPLETED ---------------------------------\n"
            )
        except Exception as e:
            print(e)
    else:
        print("No pull image parameters available.")


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
        print(
            "\n-----------------  REMOVING OPERATION COMPLETED ---------------------------------\n"
        )
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
        print(
            "\n-----------------  LISTING OPERATION COMPLETED ---------------------------------\n"
        )
    except Exception as e:
        print(e)


def wait_for_access(json_value):
    global registration_id
    print("[!] Wait for access")
    _id = json_value["command"]["value"]["id"]
    try:
        if _id == "pep-application_manager":
            purpose = json_value["command"]["value"]["message"]["purpose"]
            code = json_value["command"]["value"]["message"]["code"]
            response_id = json_value["command"]["value"]["message"][
                "message_id"
            ]
            if (
                purpose == "REGISTER_RESPONSE"
                and code == "OK"
                and response_id == registration_id
            ):
                return "OK"
            else:
                return "REGISTRATION DENIED"
    except Exception as e:
        print(e)


def on_message(ws, message):
    global REGISTERED
    global session_id
    global permit_installation
    json_message = json.loads(message)

    try:
        if "Volatile" in json_message:
            json_message = json_message["Volatile"]
            json_value = json_message["value"]
            purpose = json_value["command"]["value"]["message"]["purpose"]

            if purpose == "TRY_RESPONSE":
                print("[!] Permit Installation")
                handle_pull_image()

            if (
                json_value["command"]["value"]["topic_name"]
                == "application_manager_registration"
                and REGISTERED == False
            ):
                access = wait_for_access(json_value)
                if access == "OK":
                    REGISTERED = True
                    print(
                        "[!] REGISTRATION OK: Application Manager is registered to UC\n\n"
                    )
                else:
                    print("[!] Application Manager is not registered to UC")
    except Exception as e:
        #print("ERROR: " + str(e))
        pass

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


global_pull_image_params = None


# Funzione per salvare i parametri di handle_pull_image
def save_pull_image_params(params):
    global global_pull_image_params
    global_pull_image_params = params


def handle_message(ws, topic_uuid, topic_value, request_id, requestor_id):
    global permit_installation
    if "operation" in topic_value:
        operation = topic_value["operation"]
        if operation == "pull_image":
            print("[!] Forwarding UCS Request")
            UCS_request(ws, topic_value, topic_uuid, request_id, requestor_id)
            print("[!] Pulling Image Request")
            params = {
                "ws": ws,
                "topic_value": topic_value,
                "topic_uuid": topic_uuid,
            }
            save_pull_image_params(params)
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
    global REGISTERED
    global registration_id
    print("### Connection established ###")
    if REGISTERED == False:
        registration_id = security_by_contract.register()
        print("[!] The registration ID is : " + str(registration_id))


if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "ws://146.48.89.28:3000/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()
