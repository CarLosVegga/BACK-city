import flask
from flask.json import jsonify
from flask_cors import CORS
import json
import os
from model import *

app = flask.Flask(__name__)
cors = CORS(app)

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
    return {
        'statusCode': 201,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('Hello from Lambda!')
    }

@app.route("/step", methods=["GET"])
def queryState():
    # response = jsonify{"data": []}
    steps = []
    # Return a 15 steps batch
    for _ in range(0, 60):
        steps.append(c.step())
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({'data': (steps)})
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
