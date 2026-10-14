from flask import Flask, request, jsonify, Response
import random
import json

app = Flask(__name__)

# Fixed seed generation procedure
seed = 24
random.seed(seed)
a1 = random.uniform(-5, 5)
a2 = random.uniform(-5, 5)
a3 = random.uniform(-5, 5)
b = random.uniform(-10, 10)

# Route to handle the root URL
@app.route('/', methods=['GET'])
def home():
    msg = {
        "status": 200,
        "registration number": "FA23-BDS-024",
        "message": "Welcome to the Linear Regression Prediction API. Please use the /predict endpoint.",
        "example_usage": "/predict?x1=2&x2=3&x3=1"
    }
    return Response(json.dumps(msg, sort_keys=False), mimetype='application/json', status=200)

@app.route('/predict', methods=['GET'])
def predict():
    # If parameters are missing, return a friendly message with registration number
    if 'x1' not in request.args or 'x2' not in request.args or 'x3' not in request.args:
        msg = {
            "status": 200,
            "registration number": "FA23-BDS-024",
            "message": "The API is live! To get a prediction, please provide x1, x2, and x3 parameters in the URL.",
            "example_usage": "?x1=2&x2=3&x3=1"
        }
        return Response(json.dumps(msg, sort_keys=False), mimetype='application/json', status=200)

    try:
        # Accept input parameters
        x1 = float(request.args.get('x1'))
        x2 = float(request.args.get('x2'))
        x3 = float(request.args.get('x3'))

        # Calculate prediction
        y = (a1 * x1) + (a2 * x2) + (a3 * x3) + b

        # Dictionary maintains exact insertion order
        response_data = {
            "registration number": "FA23-BDS-024",
            "prediction": round(y, 2)
        }

        return Response(json.dumps(response_data, sort_keys=False), mimetype='application/json')

    except ValueError:
        error_msg = {
            "registration number": "FA23-BDS-024",
            "error": "Invalid input. Please ensure x1, x2, and x3 are numbers."
        }
        return Response(json.dumps(error_msg, sort_keys=False), mimetype='application/json', status=400)
    except Exception as e:
        error_msg = {
            "registration number": "FA23-BDS-024",
            "error": str(e)
        }
        return Response(json.dumps(error_msg, sort_keys=False), mimetype='application/json', status=400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)
