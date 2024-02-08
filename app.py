import subprocess
from flask import Flask, request, jsonify
import tempfile
import os

app = Flask(__name__)

@app.route('/execute/js', methods=['POST'])
def execute_js_code():
    code = request.json.get('code')
    package_json = request.json.get('package_json', None)

    with tempfile.TemporaryDirectory() as temp_dir:
        code_path = os.path.join(temp_dir, 'script.js')
        with open(code_path, 'w') as code_file:
            code_file.write(code)

        if package_json:
            package_json_path = os.path.join(temp_dir, 'package.json')
            with open(package_json_path, 'w') as package_file:
                package_file.write(package_json)

        try:
            # Combine npm install and code execution in one command
            docker_command = [
                'docker', 'run', '--rm', '-v', f"{temp_dir}:/workspace",
                'js-code-execution',
                '/bin/bash', '-c', 
                'if [ -f "package.json" ]; then npm install; fi; node script.js'
            ]
            result = subprocess.run(docker_command, capture_output=True, text=True, timeout=100)

            output = result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            output = "Execution timed out."

    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
