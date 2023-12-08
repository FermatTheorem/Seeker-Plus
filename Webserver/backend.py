from flask import Flask, render_template, jsonify
import yaml

app = Flask(__name__)

def load_yaml_data():
    with open('/home/user/PycharmProjects/Seeker-Plus/config.yaml', 'r') as file:
        return yaml.safe_load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-config')
def get_config():
    data = load_yaml_data()
    print(data)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=1234)
