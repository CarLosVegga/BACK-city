import flask
from flask.json import jsonify

from model import *

app = flask.Flask(__name__)

@app.route("/simulation", methods=["POST"])
def create():
    global c 
    c = City()
    response = jsonify({"ok": 201})
    response.status_code = 201
    response.headers['Access-Control-Expose-Headers'] = '*'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.autocorrect_location_header = False
    return response

@app.route("/step", methods=["GET"])
def queryState():
    steps = []
    # Return a 15 steps batch
    for _ in range(0, 15):
        steps.append(c.step())
    return jsonify({"data": steps})

app.run()
