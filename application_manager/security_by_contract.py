import json
import os
import subprocess


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
    command = [
        "cargo",
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


def get_labels(image_name):
    # Name of the file to execute
    script_file = "application_manager/get-labels.sh"
    sifis_prefix = "gchr.io/sifis-home/"
    version = "latest"

    try:
        # Execute the shell command with the given image name as an argument
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
        json_filename = "manifest_" + image_name + ".json"
        path = "sifis-xacml/data/"
        save_manifest_to_file(manifest_data, path + json_filename)
        run_cargo_command(json_filename)
        return manifest_data
    except subprocess.CalledProcessError as e:
        print("Error during script execution:", e)


get_labels("3pa-lamp-amd64")
