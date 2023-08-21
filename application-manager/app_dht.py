import json

import docker
import requests

client = docker.from_env()

api_url = "http://localhost:3000/"


def publish(ws, topic_uuid, requestor_id, request_id, containers):
    ws_req = {
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
    ws.send(json.dumps(ws_req))
    print("[!] Container List has been updated")
    return


def request_list(ws, message, image_name):
    json_message = json.loads(message)
    # Handle messages
    topic_name = json_message["topic_name"]
    topic_uuid = json_message["topic_uuid"]
    if topic_name == "SIFIS:container_list":
        if "value" in json_message:
            topic_value = json_message["value"]
            requestor_id = topic_value["requestor_id"]
            request_id = topic_value["request_id"]
            containers = topic_value["containers"]
            containers.append(image_name)
            publish(ws, topic_uuid, requestor_id, request_id, containers)
            print("Active Containers: " + str(containers))


def update_dht_list(ws, image_name):
    topic_name = "SIFIS:container_list"
    response = requests.get(api_url + "topic_name/" + topic_name)
    message = str(response.json()[0])
    message = message.replace("'", '"')
    if message is None:
        topic_uuid = "Pippo"
        request_id = "1"
        requestor_id = "1"
        containers = [image_name]
        publish(ws, topic_uuid, requestor_id, request_id, containers)
    else:
        request_list(ws, message, image_name)


def pull_image(ws, image_name, topic_uuid, requestor_id, request_id):
    if image_name:
        try:
            client.images.pull(image_name)
            update_dht_list(ws, image_name)
            topic_name = "SIFIS:application_manager_pull_image"
            pulling_data = {
                "requestor_id": requestor_id,
                "request_id": request_id,
                "pulled_image": image_name,
                "operation": "pull image",
                "result": "successfull",
            }
            requests.post(
                api_url
                + "topic_name/"
                + topic_name
                + "/topic_uuid/"
                + topic_uuid,
                json=pulling_data,
            )
            return f"Image {image_name} pulled successfully!"
        except docker.errors.APIError as e:
            pulling_data = {
                "requestor_id": requestor_id,
                "request_id": request_id,
                "pulled_image": image_name,
                "operation": "pull image",
                "result": "Error while pulling image {image_name}: {e}",
            }
            requests.post(
                api_url
                + "topic_name/"
                + topic_name
                + "/topic_uuid/"
                + topic_uuid,
                json=pulling_data,
            )
            return f"Error while pulling image {image_name}: {e}", 500
    else:
        return "Missing 'image_name' parameter", 400


def start_container(image_name):
    if image_name:
        try:
            container = client.containers.run(image_name, detach=True)
            return f"Container {container.id} started successfully!"
        except docker.errors.ImageNotFound as e:
            return f"Image {image_name} not found: {e}", 404
        except docker.errors.APIError as e:
            return (
                f"Error while starting container from image {image_name}: {e}",
                500,
            )
    else:
        return "Missing 'image_name' parameter", 400


def stop_container(container_id, topic_uuid, request_id, requestor_id):
    if container_id:
        try:
            container = client.containers.get(container_id)
            container.stop()
            topic_name = "SIFIS:application_manager_stop_container"
            container_info = {
                "requestor_id": requestor_id,
                "request_id": request_id,
                "container_id": container_id,
                "operation": "stop container",
                "result": "successfull",
            }
            requests.post(
                api_url
                + "topic_name/"
                + topic_name
                + "/topic_uuid/"
                + topic_uuid,
                json=container_info,
            )
            return f"Container {container_id} stopped successfully!"
        except docker.errors.NotFound as e:
            return f"Container {container_id} not found: {e}", 404
        except docker.errors.APIError as e:
            return f"Error while stopping container {container_id}: {e}", 500
    else:
        return "Missing 'container_id' parameter", 400


def remove_container(container_id):
    if container_id:
        try:
            container = client.containers.get(container_id)
            container.remove(force=True)
            return f"Container {container_id} removed successfully!"
        except docker.errors.NotFound as e:
            return f"Container {container_id} not found: {e}", 404
        except docker.errors.APIError as e:
            return f"Error while removing container {container_id}: {e}", 500
    else:
        return "Missing 'container_id' parameter", 400


def remove_image(image_name, topic_uuid, request_id, requestor_id):
    if not image_name:
        return "Missing 'image_name' parameter", 400

    try:
        client.images.remove(image_name, force=True)
        topic_name = "SIFIS:application_manager_remove_image"
        removing_info = {
            "requestor_id": requestor_id,
            "request_id": request_id,
            "image": image_name,
            "operation": "remove image",
            "result": "successfull",
        }
        requests.post(
            api_url + "topic_name/" + topic_name + "/topic_uuid/" + topic_uuid,
            json=removing_info,
        )
        list_containers(topic_uuid, requestor_id, request_id, image_name)
        return f"Image {image_name} removed successfully!"
    except docker.errors.ImageNotFound as e:
        return f"Image {image_name} not found: {e}", 404
    except docker.errors.APIError as e:
        return f"Error while removing image {image_name}: {e}", 500


def list_containers(topic_uuid, requestor_id, request_id, image_name):
    topic_name = "SIFIS:container_list"
    response = requests.get(api_url + "topic_name/" + topic_name)
    message = str(response.json()[0])
    message = message.replace("'", '"')
    if "value" in str(message):
        json_message = json.loads(message)
        topic_value = json_message["value"]
        containers = topic_value["containers"]
        if image_name != None:
            containers.remove(image_name)
        _list = {
            "requestor_id": requestor_id,
            "request_id": request_id,
            "containers": containers,
        }
    local_response = requests.post(
        api_url + "topic_name/" + topic_name + "/topic_uuid/" + topic_uuid,
        json=_list,
    )
    remote_host = "https://yggio.sifis-home.eu:3000/dht-insecure/"
    yggio_response = requests.post(
        remote_host + "topic_name/" + topic_name + "/topic_uuid/" + topic_uuid,
        json=_list,
        verify=False,
    )
    print("YGGIO Response: " + str(yggio_response.content) + "\n\n")
    return _list