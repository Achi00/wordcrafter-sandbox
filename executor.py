import os
import subprocess

def execute_js_code(js_code, cache_path):
    script_path = os.path.join(cache_path, 'script.js')
    
    if not os.path.exists(cache_path):
        print(f"Cache path does not exist: {cache_path}")
        return "Directory creation failed."
    
    try:
        with open(script_path, 'w') as script_file:
            script_file.write(js_code)
    except Exception as e:
        print(f"Failed to write js code to script.js: {e}")
        return "Failed to write js code."

    # Convert to absolute path
    absolute_cache_path = os.path.abspath(cache_path)

    docker_command = [
        'docker', 'run', '--rm', '-v', f"{absolute_cache_path}:/workspace",
        'js-code-execution',  # Ensure this is your correct Docker image name
        '/workspace/run-code.sh', 'script.js'
    ]

    result = subprocess.run(docker_command, capture_output=True, text=True, check=True)
    return result.stdout if result.returncode == 0 else result.stderr
