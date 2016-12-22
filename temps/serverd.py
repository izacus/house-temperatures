from flask import Flask, jsonify
from flask import redirect
from flask import request
from flask import send_from_directory

from database import get_current_status, get_graphing_data

from werkzeug.contrib.cache import SimpleCache

CACHE_TIMEOUT = 300

cache = SimpleCache()
app = Flask(__name__)


@app.route("/current_status")
def status():
    response = cache.get(request.path)
    if response is None:
        response = jsonify(get_current_status())
        cache.set(request.path, response, CACHE_TIMEOUT)
    return response


@app.route("/graph/<int:room_number>")
def hourly_graph_data(room_number):
    response = cache.get(request.path)
    if response is None:
        response = jsonify(get_graphing_data(room_number))
        cache.set(request.path, response, CACHE_TIMEOUT)
    return response


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("../static", path)


@app.route("/")
def index():
    return redirect("/index.html", code=302)


if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0")