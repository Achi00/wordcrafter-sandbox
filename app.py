import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/execute-js', methods=['POST'])
def execute_js_code():
    code = request.json.get('code')
    
    # Prepare the Docker run command for JavaScript
    run_cmd = [ 
        'docker', 'run', '--rm',
        '-i',  # Keep STDIN open to send code
        'js-execution-sandbox',  # Image name
        'node', '-e', code  # Execute JS code directly
    ]
    
    # Execute the command and capture output
    result = subprocess.run(run_cmd, capture_output=True, text=True)
    
    # Check for errors
    if result.returncode == 0:
        output = result.stdout
    else:
        output = result.stderr
    
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
