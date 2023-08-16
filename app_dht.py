import docker

import send_data

client = docker.from_env()


def pull_image(image_name, uuid, requestor_id, request_id):
    if image_name:
        try:
            client.images.pull(image_name)
            operation = "pull_image"
            send_data.send_data(
                image_name, operation, uuid, requestor_id, request_id
            )
            # print(f"Image {image_name} pulled successfully!")
            return f"Image {image_name} pulled successfully!"
        except docker.errors.APIError as e:
            return f"Error while pulling image {image_name}: {e}", 500
    else:
        return "Missing 'image_name' parameter", 400


def start_container(image_name, uuid, requestor_id, request_id):
    if image_name:
        try:
            container = client.containers.run(image_name, detach=True)
            operation = "start_image"
            send_data.send_data(
                image_name, operation, uuid, requestor_id, request_id
            )
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


def stop_container(container_id, uuid, requestor_id, request_id):
    if container_id:
        try:
            container = client.containers.get(container_id)
            operation = "stop_container"
            container.stop()
            send_data.send_data(
                container_id, operation, uuid, requestor_id, request_id
            )
            return f"Container {container_id} stopped successfully!"
        except docker.errors.NotFound as e:
            return f"Container {container_id} not found: {e}", 404
        except docker.errors.APIError as e:
            return f"Error while stopping container {container_id}: {e}", 500
    else:
        return "Missing 'container_id' parameter", 400


def remove_container(container_id, uuid, requestor_id, request_id):
    if container_id:
        try:
            container = client.containers.get(container_id)
            container.remove(force=True)
            operation = "remove_container"
            send_data.send_data(
                container_id, operation, uuid, requestor_id, request_id
            )
            return f"Container {container_id} removed successfully!"
        except docker.errors.NotFound as e:
            return f"Container {container_id} not found: {e}", 404
        except docker.errors.APIError as e:
            return f"Error while removing container {container_id}: {e}", 500
    else:
        return "Missing 'container_id' parameter", 400


def remove_image(image_name, uuid, requestor_id, request_id):
    if not image_name:
        return "Missing 'image_name' parameter", 400

    try:
        client.images.remove(image_name, force=True)
        operation = "remove_image"
        send_data.send_data(
            image_name, operation, uuid, requestor_id, request_id
        )
        return f"Image {image_name} removed successfully!"
    except docker.errors.ImageNotFound as e:
        return f"Image {image_name} not found: {e}", 404
    except docker.errors.APIError as e:
        return f"Error while removing image {image_name}: {e}", 500


def list_containers(uuid, requestor_id, request_id):
    containers = client.containers.list()
    container_list = [f"{c.id} ({c.name})" for c in containers]
    operation = "list_containers"
    image_name = "None"
    send_data.send_data(
        image_name, operation, uuid, requestor_id, request_id, container_list
    )
    return container_list
