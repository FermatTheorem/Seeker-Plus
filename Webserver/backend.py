from flask import Flask, render_template, jsonify, request, send_from_directory
import yaml
import os

app = Flask(__name__)
app.json.sort_keys = False

def load_yaml_data():
    with open('/home/user/PycharmProjects/Seeker-Plus/config.yaml', 'r') as file:
        return yaml.safe_load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-config')
def get_config():
    data = load_yaml_data()
    return jsonify(data)

@app.route('/save-config', methods=["POST"])
def save_config():
    res = yaml.dump(request.get_json(), sort_keys=False)
    # print(res)
    return jsonify({"status": "ok"})


@app.route('/output/<path:filename>')
def file_contents(filename):
    filename = "../"+filename
    if not os.path.exists(filename) or not os.path.isfile(filename):
        return "404 Not Found", 404

    with open(filename, 'r') as file:
        file_contents = file.read()

    # Return the contents with the appropriate MIME type
    return file_contents, 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=1234)
