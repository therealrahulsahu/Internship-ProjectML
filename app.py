from flask import Flask, request
# from PartialPaymentPredictor import _1705157
import pickle
import json
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

# payment = _1705157()
# payment.load_data_from_db("project")
# payment.prepare_dict()
payment = pickle.load(open("PartialPaymentPredictor/1705157.pkl", 'rb'))


@app.route('/get_prediction_by_pk_id', methods=['POST', 'GET'])
def get_prediction_by_pk_id():
    pk_id = 0
    if request.method == 'POST':
        pk_id = int(request.form['pk_id'])
    if request.method == 'GET':
        pk_id = int(request.args.get('pk_id'))

    response = payment.get_prediction_of_pk_id(pk_id)
    return json.dumps(response)


if __name__ == '__main__':
    app.run()
    # pickle.dump(open("PartialPaymentPredictor/1705157.pkl", 'wb'))
