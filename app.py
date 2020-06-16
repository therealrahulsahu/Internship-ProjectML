from flask import Flask, request
from PartialPaymentPredictor import PaymentPredictor

app = Flask(__name__)

payment = PaymentPredictor()
payment.load_data_from_db("project")
payment.prepare_dict()


@app.route('/get_prediction_by_pk_id', methods=['POST', 'GET'])
def get_prediction_by_pk_id():
    pk_id = 0
    if request.method == 'POST':
        pk_id = int(request.form['pk_id'])
        return payment.get_prediction_of_pk_id(pk_id)
    if request.method == 'GET':
        pk_id = int(request.args.get('pk_id'))
    return payment.get_prediction_of_pk_id(pk_id)


if __name__ == '__main__':
    app.run()
