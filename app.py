from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import tempfile
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug', methods=['POST'])
def debug_code():
    print("Received debug request")
    try:
        data = request.json
        print(f"Received data: {data}")
        code = data['code']
        language = data['language']
    except Exception as e:
        print(f"Error parsing request: {e}")
        return jsonify({'error': 'Invalid request data'}), 400

    if language not in ['python', 'javascript']:
        return jsonify({'error': 'Unsupported language'}), 400

    with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        if language == 'python':
            result = subprocess.run(['python', temp_file_path], capture_output=True, text=True, timeout=5)
        elif language == 'javascript':
            result = subprocess.run(['node', temp_file_path], capture_output=True, text=True, timeout=5)

        output = result.stdout
        error = result.stderr

        print(f"Execution result - Output: {output}, Error: {error}")

        return jsonify({
            'output': output,
            'error': error
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Execution timed out'}), 408
    except Exception as e:
        print(f"Execution error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(temp_file_path)

if __name__ == '__main__':
    app.run(debug=True)