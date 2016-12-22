from flask import Flask, jsonify
from flask import redirect
from flask import send_from_directory
from flask import url_for

from temps.database import get_current_status, get_graphing_data

app = Flask(__name__)


@app.route("/current_status")
def status():
    status_data = get_current_status()
    return jsonify(status_data)


@app.route("/graph/<room_number>")
def hourly_graph_data(room_number):
    return jsonify(get_graphing_data(room_number))


@app.route("/<path:path>")
def index(path):
    return send_from_directory("../static", path)


if __name__=="__main__":
    app.run(debug=True)