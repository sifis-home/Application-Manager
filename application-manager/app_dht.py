import docker
import io
from io import BytesIO

client = docker.from_env()

def pull_image(image_name):
    if image_name:
        try:
            client.images.pull(image_name)
            #print(f"Image {image_name} pulled successfully!")
            return f"Image {image_name} pulled successfully!"
        except docker.errors.APIError as e:
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
            return f"Error while starting container from image {image_name}: {e}", 500
    else:
        return "Missing 'image_name' parameter", 400


def stop_container(container_id):
    if container_id:
        try:
            container = client.containers.get(container_id)
            container.stop()
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

def remove_image(image_name):
    if not image_name:
        return "Missing 'image_name' parameter", 400

    try:
        client.images.remove(image_name, force=True)
        return f"Image {image_name} removed successfully!"
    except docker.errors.ImageNotFound as e:
        return f"Image {image_name} not found: {e}", 404
    except docker.errors.APIError as e:
        return f"Error while removing image {image_name}: {e}", 500


def list_containers():
    containers = client.containers.list()
    container_list = [f"{c.id} ({c.name})" for c in containers]
    return container_list
