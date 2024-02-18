from flask import Flask, request, jsonify
import os
import subprocess
import hashlib
from datetime import datetime
from db_client import save_execution_metadata, get_execution_metadata_by_hash, get_user_plan, chat_exists
import time

app = Flask(__name__)

def generate_unique_execution_hash(user_code, package_json, user_id, chat_id):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_input = user_code + package_json + user_id + chat_id + current_time
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

def execute_script(target_path, user_code, package_json):
    started_at = datetime.utcnow()
    try:
        docker_command = [
            'docker', 'run', '--rm', '-v', f"{target_path}:/workspace",
            'sandbox-runner',  # Ensure you have built your Docker image with this tag
            '/bin/bash', '-c',
            'if [ -f "package.json" ]; then npm install; fi; node script.js'
        ]
        result = subprocess.run(docker_command, capture_output=True, text=True, check=True, timeout=30)
        ended_at = datetime.utcnow()

        execution_details = {
            "status": "success",
            "output": result.stdout,
            "startedAt": started_at,
            "endedAt": ended_at
        }
        # Here, consider saving execution metadata or returning it as part of the response
        return jsonify({"output": result.stdout}), 200
    except subprocess.CalledProcessError as e:
        ended_at = datetime.utcnow()
        execution_details = {
            "status": "error",
            "error": e.stderr,
            "startedAt": started_at,
            "endedAt": ended_at
        }
        return jsonify({"error": e.stderr}), 500
    except subprocess.TimeoutExpired as e:
        ended_at = datetime.utcnow()
        execution_details = {
            "status": "error",
            "error": "Execution timed out.",
            "startedAt": started_at,
            "endedAt": ended_at
        }
        return jsonify({"error": "Execution timed out."}), 500


def handle_free_user_execution(user_id, data):
    user_code = data['code']
    package_json = data.get('packageJson', '{}')

    # Define the path for free users. This assumes all free users share a single node_modules directory under their user ID.
    base_path = os.path.abspath("./node_modules_cache")
    target_path = os.path.join(base_path, "free", user_id)  # Use a 'free' subdirectory to distinguish free user data

    # Ensure the directory exists
    os.makedirs(target_path, exist_ok=True)

    # Write the user's code and package.json to the target directory
    with open(os.path.join(target_path, 'script.js'), 'w') as script_file:
        script_file.write(user_code)
    with open(os.path.join(target_path, 'package.json'), 'w') as package_file:
        package_file.write(package_json)

    # Execute the script using the modified Docker command
    return execute_script(target_path, user_code, package_json)


def handle_plus_user_execution(user_id, chat_id, data):
    user_code = data['code']
    package_json = data.get('packageJson', '{}')
    execution_hash = generate_unique_execution_hash(user_code, package_json, user_id, chat_id)

    base_path = os.path.abspath("./node_modules_cache")
    target_path = os.path.join(base_path, "plus", user_id, chat_id, execution_hash)  # Distinguish plus user data with a 'plus' subdirectory

    os.makedirs(target_path, exist_ok=True)
    with open(os.path.join(target_path, 'script.js'), 'w') as script_file:
        script_file.write(user_code)
    with open(os.path.join(target_path, 'package.json'), 'w') as package_file:
        package_file.write(package_json)

    return execute_script(target_path, user_code, package_json)


@app.route('/execute-js', methods=['POST'])
def execute_js():
    data = request.json
    user_plan = get_user_plan(data.get('userId'))
    if user_plan == "free":
        return handle_free_user_execution(data.get('userId'), data)
    elif user_plan == "plus":
        return handle_plus_user_execution(data.get('userId'), data.get('chatId'), data)
    else:
        return jsonify({"error": "Invalid user plan or user not found"}), 400

    
    # Generate a unique execution hash
    # current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    # hash_input = user_code + package_json + user_id + chat_id + current_time
    # execution_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

    # target_path = generate_unique_execution_path(user_id, chat_id)

    # os.makedirs(target_path, exist_ok=True)
    # with open(os.path.join(target_path, 'script.js'), 'w') as file:
    #     file.write(user_code)
    # with open(os.path.join(target_path, 'package.json'), 'w') as file:
    #     file.write(package_json)

    # started_at = datetime.utcnow()
    # try:
    #     docker_command = [
    #             'docker', 'run', '--rm', '-v', f"{target_path}:/workspace",
    #             'sandbox-runner',
    #             '/bin/bash', '-c', 
    #             'if [ -f "package.json" ]; then npm install; fi; node script.js'
    #     ]

    #     result = subprocess.run(docker_command, capture_output=True, text=True, check=True, timeout=30)
    #     ended_at = datetime.utcnow()
    #     # Save successful execution metadata
    #     execution_details = {
    #         "executionHash": execution_hash,
    #         "status": "success",
    #         "output": result.stdout,
    #         "startedAt": started_at,
    #         "endedAt": ended_at
    #     }
    #     save_execution_metadata(user_id, chat_id, execution_details)
    #     return jsonify({"output": result.stdout}), 200
    # except subprocess.CalledProcessError as e:
    #     ended_at = datetime.utcnow()
    #     # Save failed execution metadata
    #     execution_details = {
    #         "executionHash": execution_hash,
    #         "status": "error",
    #         "error": e.stderr,
    #         "startedAt": started_at,
    #         "endedAt": ended_at
    #     }
    #     save_execution_metadata(user_id, chat_id, execution_details)
    #     return jsonify({"error": e.stderr}), 500
    # except subprocess.TimeoutExpired:
    #     ended_at = datetime.utcnow()
    #     # Save timeout execution metadata
    #     execution_details = {
    #         "executionHash": execution_hash,
    #         "status": "error",
    #         "error": "Execution timed out.",
    #         "startedAt": started_at,
    #         "endedAt": ended_at
    #     }
    #     save_execution_metadata(user_id, chat_id, execution_details)
    #     return jsonify({"error": "Execution timed out."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
