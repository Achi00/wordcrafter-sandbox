from flask import Flask, request, jsonify
from dependency_manager import generate_package_hash, get_cache_path, install_dependencies_and_save_cache
from executor import execute_js_code
from db_client import check_and_reuse_cache, save_cache_metadata
import json

app = Flask(__name__)

@app.route('/execute/js', methods=['POST'])
def execute_js_code_endpoint():
    data = request.json
    userId = data['userId']
    chatId = data['chatId']
    package_json = data.get('package_json', '{}')

    package_hash = generate_package_hash(package_json)
    cache_path = get_cache_path(userId, chatId, package_hash)

    try:
        if not check_and_reuse_cache(userId, chatId, package_hash):
            result = install_dependencies_and_save_cache(package_json, cache_path, userId, chatId, package_hash)
            if result is not None:
                return jsonify({"error": result}), 500
    except Exception as e:
        print(f"Exception during dependency installation and cache setup: {e}")
        return jsonify({"error": "Exception during dependency installation and cache setup."}), 500

    output = execute_js_code(data['code'], cache_path)
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
