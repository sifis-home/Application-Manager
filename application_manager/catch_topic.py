import json

import app_dht
import requests
import security_by_contract
import websocket

REGISTERED = False
registration_id = 1
session_id = "None"
permit_installation = False


def get_messages():
    return security_by_contract.messages


def UCS_request(ws, topic_name, topic_uuid, request_id, requestor_id):
    global REGISTERED, session_id
    try:
        image_name = topic_name["image_name"]
        image_name = image_name.replace("ghcr.io/sifis-home/", "").replace(
            ":latest", ""
        )
        print("[!] Recovering App LABELS\n")
        _, app_id = security_by_contract.get_labels(image_name)
        session_id = app_id
        if session_id == "None":
            notify_mobile_application(message=None)
        else:
            print("[!] APP_ID: " + str(session_id))
            return
    except Exception as e:
        print(e)


def send_installation_results(description, request_id, result):
    address = "http://localhost:3000/"
    topic_name = "SIFIS:mobile-application"
    topic_uuid = "installation-results"
    permission_data = {
        "result": result,
        "request_id": request_id,
        "description": description,
    }
    requests.post(
        address + "topic_name/" + topic_name + "/topic_uuid/" + topic_uuid,
        json=permission_data,
    )
    print("\n[!] Installation Result sent: " + str(result) + "\n")
    return


def notify_mobile_application(message):
    global global_pull_image_params
    params = global_pull_image_params

    topic_name = "SIFIS:notification_message"
    if params is not None:
        topic_value = params["topic_value"]
        topic_uuid = params["topic_uuid"]
        try:
            image_name = topic_value["image_name"]
            try:
                image_name = image_name.replace(
                    "ghcr.io/sifis-home/", ""
                ).replace(":latest", "")
            except:
                pass
            requestor_id = topic_value["requestor_id"]
            request_id = topic_value["request_id"]
        except Exception as e:
            print(e)
    if message == None:
        notification = (
            "The "
            + image_name
            + " cannot be installed, the operation is NOT permitted by Usage Control"
        )
    else:
        notification = (
            image_name + " " + message
        )  # The application can be installed
    print("[!] " + notification)
    address = "http://localhost:3000/"
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
                image_name = image_name.replace(
                    "ghcr.io/sifis-home/", ""
                ).replace(":latest", "")
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
        image_name = image_name.replace(":latest", "")
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

    messages = get_messages()

    try:
        if "Volatile" in json_message:
            json_message = json_message["Volatile"]
            json_value = json_message["value"]
            purpose = json_value["command"]["value"]["message"]["purpose"]

            if purpose == "TRY_RESPONSE":
                message_id = json_value["command"]["value"]["message"][
                    "message_id"
                ]
                evaluation = json_value["command"]["value"]["message"][
                    "evaluation"
                ]
                try:
                    if message_id in messages:
                        messages.remove(message_id)
                except Exception as e:
                    print(e)
                if evaluation == "Deny":
                    security_by_contract.denied_messages.append(message_id)
                else:
                    security_by_contract.permit_messages.append(message_id)

                num_responses = len(
                    security_by_contract.denied_messages
                ) + len(security_by_contract.permit_messages)
                if num_responses == security_by_contract.num_request:
                    if (
                        len(security_by_contract.permit_messages)
                        == security_by_contract.num_request
                    ):
                        print("[!] Permit Installation")
                        handle_pull_image()
                        request_id = security_by_contract.get_request_id()
                        send_installation_results(
                            "null", request_id, "installed"
                        )
                    else:
                        notify_mobile_application(
                            message="Application not compliant"
                        )
                        device_action = []
                        for deny_id in security_by_contract.denied_messages:
                            for (
                                id,
                                req,
                            ) in security_by_contract.request_message_mapping:
                                if id == deny_id:
                                    # request_id = security_by_contract.get_request_id()
                                    request = str(req)
                                    device_type = request.split(
                                        '<Attribute AttributeId="eu.sifis-home:1.0:resource:device:device-type" IncludeInResult="false">',
                                        1,
                                    )[1].split("</AttributeValue>")[0]
                                    device_type = device_type.split(
                                        '<AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">',
                                        1,
                                    )[1]
                                    print("DEVICE: ", device_type)
                                    action_id = request.split(
                                        '<Attribute AttributeId="eu.sifis-home:1.0:resource:device:action:action-id" IncludeInResult="false">',
                                        1,
                                    )[1].split("</AttributeValue>")[0]
                                    action_id = action_id.split(
                                        '<AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">',
                                        1,
                                    )[1]
                                    action_id = action_id.replace("_", " ")
                                    print("ACTION_ID: " + action_id)
                                    device_action.append(
                                        (device_type, action_id)
                                    )
                        mess_first_part = "\nIn particular, "
                        mess_second_part = "is not allowed."
                        mess = ""

                        for device, action in device_action:
                            new_mess = (
                                'the operation "'
                                + action
                                + '" on the device "'
                                + device
                                + '", '
                            )
                            mess = mess + new_mess

                        final_mess = mess_first_part + mess + mess_second_part
                        print(final_mess)
                        request_id = security_by_contract.get_request_id()
                        send_installation_results(
                            "\nYour security policies prevent the app from being installed. "
                            + final_mess,
                            request_id,
                            "not-compliant",
                        )
                    security_by_contract.permit_messages = []
                    security_by_contract.denied_messages = []
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
        # print("ERROR: " + str(e))
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
        if operation == "install_anyway":
            print("\n[!] User chose to install the Application Anyway !!!\n")
            handle_pull_image()
            send_installation_results("null", request_id, "installed")

        if operation == "abort":
            print("\n[!] User chose to abort the installation !!!\n")
            send_installation_results("null", request_id, "aborted")
        if operation == "pull_image":
            security_by_contract.set_request_id(request_id)
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
        "ws://localhost:3000/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()
