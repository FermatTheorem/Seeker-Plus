from flask import Flask, render_template, jsonify, request
import yaml
from Engine.Engine import Engine
from config import CONFIG

app = Flask(__name__)
app.json.sort_keys = False


def load_config():
    with Engine.open_file("config.yaml") as f:
        return yaml.safe_load(f)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get-config')
def get_config():
    data = load_config()
    return jsonify(data)


@app.route('/save-config', methods=["POST"])
def save_config():
    res = yaml.dump(request.get_json(), sort_keys=False)
    Engine.file_write("config.yaml", res, CONFIG["General"]["root_directory"])
    return jsonify({"status": "ok"})


@app.route('/output/<path:filename>')
def show_file_contents(filename):
    with Engine.open_file(filename, Engine.get_output_dir()) as file:
        file_contents = file.read()

    return file_contents, 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=1234)

