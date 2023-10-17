import base64
import datetime
import json
import os
import subprocess
import uuid
from pathlib import Path

import requests

REGISTERED = False
websocket_uri = "http://localhost:3000/"
messages = []
denied_messages = []
num_request = 0
permit_messages = []
request_message_mapping = []
request_id = None


def set_request_id(sent_request_id):
    global request_id
    request_id = sent_request_id


def get_request_id():
    global request_id
    return request_id


def set_request_message_mapping(tuple):
    global request_message_mapping
    request_message_mapping.append(tuple)
    return request_message_mapping


def set_num_request(num):
    global num_request
    num_request = num


def set_messages(message_id):
    global messages
    messages.append(message_id)


def get_json_register():
    ws_req = {
        "timestamp": int(datetime.datetime.now().timestamp() * 1000),
        "command": {
            "command_type": "pep-command",
            "value": {
                "message": {
                    "purpose": "REGISTER",
                    "message_id": str(uuid.uuid1()),
                    "sub_topic_name": "application_manager_registration",
                    "sub_topic_uuid": "application_manager_registration_uuid",
                },
                "id": "pep-application_manager",
                "topic_name": "topic-name",
                "topic_uuid": "topic-uuid-the-ucs-is-subscribed-to",
            },
        },
    }
    print("\n---------- REGISTRATION ATTEMPT ------------\n")
    message_id = ws_req["command"]["value"]["message"]["message_id"]
    return ws_req, message_id


def register():
    req, id = get_json_register()
    requests.post(websocket_uri + "pub", json=req)
    REGISTERED = True
    return id


def extract_manifest_json(output):
    start_index = output.find("Label: manifest\n") + len("Label: manifest\n")
    end_index = output.find("Label:", start_index)
    manifest_json = output[start_index:end_index].strip()
    return manifest_json


def save_manifest_to_file(data, filename):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=2)


def create_third_party_folder(source_path, json_filename):
    folder_path = "./" + json_filename.replace(".json", "")
    try:
        os.makedirs(source_path + "/" + folder_path, exist_ok=True)
        print(f"Folder '{folder_path}' created.")
    except OSError as e:
        print("Error creating folder:", e)


def run_cargo_command(json_filename):
    folder_path = "sifis-xacml"
    create_third_party_folder(folder_path, json_filename)

    # Get the user's home directory and expand ~ to the full path
    home_directory = os.path.expanduser("~")

    # Construct the full path to the cargo executable
    cargo_executable = os.path.join(home_directory, ".cargo", "bin", "cargo")

    command = [
        cargo_executable,
        "run",
        "--",
        "-a",
        "data/" + json_filename,
        "-o",
        "./" + json_filename.replace(".json", ""),
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=folder_path,
        )
        print("Command output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Command output (stderr):", e.stderr)


def xml_to_base64(xml_file_path):
    try:
        request = Path(xml_file_path).read_text()
        print("XACML request used:")
        b = base64.b64encode(bytes(request, "utf-8"))  # bytes
        request64 = b.decode("utf-8")

        return request64

    except Exception as e:
        return str(e)


def organize_json(request_base64):
    ws_req = {
        "timestamp": int(datetime.datetime.now().timestamp() * 1000),
        "command": {
            "command_type": "pep-command",
            "value": {
                "message": {
                    "purpose": "TRY",
                    "message_id": str(uuid.uuid1()),
                    "request": request_base64,
                    "policy": None,
                },
                "id": "pep-application_manager",
                "topic_name": "topic-name",
                "topic_uuid": "topic-uuid-the-ucs-is-subscribed-to",
            },
        },
    }
    return ws_req


def get_labels(image_name):
    # Name of the file to execute
    script_file = "application_manager/get-labels.sh"
    sifis_prefix = "gchr.io/sifis-home/"
    version = "latest"

    try:
        # Execute the shell command with the given image name as an argument
        manifest_data = _extract_labels(image_name, script_file, sifis_prefix, version)
        json_filename = "manifest_" + image_name + ".json"
        path = "sifis-xacml/data/"
        save_manifest_to_file(manifest_data, path + json_filename)
        run_cargo_command(json_filename)
        source_path = "sifis-xacml/manifest_"
        complete_path = source_path + image_name + "/"
        files = os.listdir(complete_path)
        set_num_request(len(files))
        for file in files:
            file_path = complete_path + file
            formatted_json, message_id = handle_xcml_request(file_path)
            set_messages(message_id)
            requests.post(websocket_uri + "pub", json=formatted_json)
        return json_filename, message_id
    except subprocess.CalledProcessError as e:
        print("Error during script execution:", e)


def _extract_labels(image_name, script_file, sifis_prefix, version):
    completed_process = subprocess.run(
        ["bash", script_file, sifis_prefix + image_name, version],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    # Get the output of the execution
    output = completed_process.stdout

    # Extract the JSON under the "manifest" label
    manifest_json = extract_manifest_json(output)

    # Parse the extracted JSON
    manifest_data = json.loads(manifest_json)

    # Print or process the extracted JSON data
    print("Extracted Manifest JSON:")
    print(json.dumps(manifest_data, indent=2))
    return manifest_data


def handle_xcml_request(file_path):
    # file_path = source_path + image_name + "/request_1.xml"
    base64_content = xml_to_base64(file_path)
    organized_json = organize_json(base64_content)
    print(json.dumps(organized_json, indent=2))
    message_id = organized_json["command"]["value"]["message"]["message_id"]
    request = Path(file_path).read_text()
    tup = (message_id, request)
    set_request_message_mapping(tup)

    return organized_json, message_id


"""
register()
get_labels("3pa-lamp-amd64")
"""
