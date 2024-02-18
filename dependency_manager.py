import os
import subprocess
import hashlib
import json
from db_client import save_cache_metadata

def generate_package_hash(package_json):
    return hashlib.sha256(json.dumps(package_json, sort_keys=True).encode()).hexdigest()

def get_cache_path(userId, chatId, package_hash):
    base_path = os.path.abspath("./node_modules_cache")  # Absolute path
    return os.path.join(base_path, userId, chatId, package_hash)


def install_dependencies_and_save_cache(package_json, cache_path, userId, chatId, package_hash):
    try:
        os.makedirs(cache_path, exist_ok=True)
        print(f"Directory successfully created or already exists: {cache_path}")
    except Exception as e:
        print(f"Failed to create directory: {e}")
        return "Failed to create directory."
    
    package_json_path = os.path.join(cache_path, "package.json")
    try:
        with open(package_json_path, "w") as f:
            f.write(package_json)
    except Exception as e:
        print(f"Failed to write package.json: {e}")
        return "Failed to write package.json."
    
    try:
        docker_command = [
            'docker', 'run', '--rm', '-v', f"{cache_path}:/workspace",
            'node:14',  # Ensure this is the correct image tag
            '/bin/bash', '-c', 'npm install'
        ]
        subprocess.run(docker_command, check=True)
        print("Docker command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Docker command failed: {e.output}")
        return "Docker command failed."

    save_cache_metadata(userId, chatId, package_hash, cache_path)
