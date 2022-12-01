import flask
from flask.json import jsonify
import os
from model import *

app = flask.Flask(__name__)

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def root():
    return jsonify([{"message":"Hello World from IBM Cloud!!!"}])

@app.route("/simulation", methods=["POST"])
def create():
    global c 
    c = City()
    response = jsonify({"Commit control": "ok"})
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
