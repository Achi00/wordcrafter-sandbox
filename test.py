from flask import Flask, request, jsonify
import os
import subprocess
import hashlib
from datetime import datetime
from db_client import save_execution_metadata, get_execution_metadata_by_hash, get_user_plan, chat_exists
import shutil
import time
import json

app = Flask(__name__)

def get_installed_packages(target_path):
    # Open and read the package-lock.json file
    with open(f"{target_path}/package-lock.json", 'r') as f:
        package_lock = json.load(f)  # Parse the file as JSON
    
    # Extract dependencies from the package-lock.json
    dependencies = package_lock.get("dependencies", {})
    
    # Return a dictionary of package names and their versions
    return {pkg: details["version"] for pkg, details in dependencies.items()}

def generate_unique_execution_hash(user_code, package_json, user_id, chat_id):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_input = user_code + package_json + user_id + chat_id + current_time
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

def execute_script(target_path, user_code, package_json):
    execution_details = {}
    started_at = datetime.utcnow()
    execution_details['startedAt'] = started_at.isoformat()
    
    try:
        start_time = time.time()
        docker_command = [
            'docker', 'run', '--rm', '-v', f"{target_path}:/workspace",
            'sandbox-runner',  # Assuming 'sandbox-runner' is your custom Docker image
            '/bin/bash', '-c',
            'npm install && node script.js'
        ]
        result = subprocess.run(docker_command, capture_output=True, text=True, check=True, timeout=30)
        end_time = time.time()
        
        # After running the script, get the installed packages
        installed_packages = get_installed_packages(target_path)  # Call the function here
        
        ended_at = datetime.utcnow()
        execution_details['endedAt'] = ended_at.isoformat()
        execution_details['duration'] = end_time - start_time
        execution_details['status'] = "success"
        execution_details['output'] = result.stdout
        execution_details['installedPackages'] = installed_packages  # Add installed packages to details
    except subprocess.CalledProcessError as e:
        execution_details['status'] = "error"
        execution_details['error'] = e.stderr
    except subprocess.TimeoutExpired as e:
        execution_details['status'] = "error"
        execution_details['error'] = "Execution timed out."
    
    return execution_details

def handle_free_user_execution(user_id, data):
    user_code = data['code']
    package_json = data.get('packageJson', '{}')
    
    # Define the base path for storing user data
    base_path = os.path.abspath("./node_modules_cache/free")
    user_path = os.path.join(base_path, user_id)  # Path for the specific user
    
    # Ensure the user directory exists, clear it if it does
    if os.path.exists(user_path):
        shutil.rmtree(user_path)
    os.makedirs(user_path, exist_ok=True)
    
    # Paths for the user's script.js and package.json
    script_path = os.path.join(user_path, 'script.js')
    package_json_path = os.path.join(user_path, 'package.json')
    
    # Write the user's code and package.json to the target directory
    with open(script_path, 'w') as script_file:
        script_file.write(user_code)
    with open(package_json_path, 'w') as package_file:
        package_file.write(package_json)
    
    # Proceed to execute the script, which includes running 'npm install'
    return execute_script(user_path, user_code, package_json)


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
    data = request.json  # Retrieves the JSON data sent to the endpoint
    user_id = data.get('userId')
    chat_id = data.get('chatId')

    # Check if the user exists and get their plan
    user_plan = get_user_plan(user_id)
    if user_plan is None:
        return jsonify({"error": "User not found"}), 404

    # Check if the chat exists (for all users)
    if not chat_exists(chat_id):  
        return jsonify({"error": "Chat not found"}), 404

    # Execute the user's code based on their plan
    if user_plan == "free":
        execution_details = handle_free_user_execution(user_id, data)
        return jsonify(execution_details)  # Return the execution details as JSON
    elif user_plan == "plus":
        execution_details = handle_plus_user_execution(user_id, chat_id, data)
        return jsonify(execution_details)  # Return the execution details as JSON
    else:
        return jsonify({"error": "Invalid user plan"}), 400
    
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
