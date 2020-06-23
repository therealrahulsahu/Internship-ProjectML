from flask import Flask, request
import pickle
import json
from flask_cors import CORS, cross_origin
# from Files import _1705157

# payment = _1705157()
# pickle.dump(payment, open("Files/1705157.pkl", 'wb'))
payment = pickle.load(open("Files/1705157.pkl", 'rb'))

app = Flask(__name__)
cors = CORS(app, support_credentials=True)


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        data = request.json['data']
        print(data)
        response = payment.getPredictions(data)
        return json.dumps(response)


if __name__ == '__main__':
    app.run(threaded=True)
