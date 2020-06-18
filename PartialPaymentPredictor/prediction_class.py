import mysql.connector as cnn
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


class _1705157:
    def __init__(self):
        self.test = pd.DataFrame([])
        self.train = pd.DataFrame([])
        self.final = pd.DataFrame([])
        self.mapped_result = {}

    def load_data_from_db(self, database, host="localhost", user="root", password="root"):
        try:
            my_db = cnn.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            my_cs = my_db.cursor()

            train_columns = ["pk_id", "customer_number", "cust_payment_terms",
                             "total_open_amount", "paid_amount", "clearing_date", "invoice_id"]
            train_query = "select pk_id, customer_number, cust_payment_terms, total_open_amount, paid_amount," \
                          " clearing_date, invoice_id from customer_invoice where clearing_date is not null order" \
                          " by clearing_date;"
            my_cs.execute(train_query)
            train_tuples = list(my_cs.fetchall())

            self.train = pd.DataFrame(train_tuples, columns=train_columns)

            test_columns = ["pk_id", "customer_number", "cust_payment_terms", "total_open_amount",
                            "invoice_amount_doc_currency"]
            test_query = "select pk_id, customer_number, cust_payment_terms, total_open_amount," \
                         " invoice_amount_doc_currency from customer_invoice where clearing_date is null;"
            my_cs.execute(test_query)
            test_tuples = list(my_cs.fetchall())

            self.test = pd.DataFrame(test_tuples, columns=test_columns)
        except Exception as e:
            print(e)

        # print(len(self.train), len(self.test))

    def pre_process_model(self):
        self.train = self.train.drop_duplicates(subset='invoice_id', keep='first')

        coded_mean = self.train.groupby('customer_number').mean().paid_amount

        self.train['mean_code'] = self.train.customer_number.map(coded_mean)
        self.test['mean_code'] = self.test.customer_number.map(coded_mean)

    def train_model(self):

        x_train = self.train[["mean_code", "cust_payment_terms", "total_open_amount"]]
        y_train = self.train[['paid_amount']]

        x_test = self.test[["mean_code", "cust_payment_terms", "total_open_amount"]]

        # SVR
        sc = StandardScaler()
        x_sc_train = sc.fit_transform(x_train)
        x_sc_test = sc.fit_transform(x_test)
        y_sc_train = sc.fit_transform(y_train)

        # Fitting SVR to the dataset
        reg = SVR(kernel='rbf')
        reg.fit(x_sc_train, y_sc_train)

        # Predicting a new result
        y_pred = sc.inverse_transform(reg.predict(x_sc_test))

        x_test['prediction'] = y_pred

        self.final = x_test[['prediction']]
        self.final['pk_id'] = self.test.pk_id
        self.final['invoice_amount_doc_currency'] = self.test.invoice_amount_doc_currency

    def prepare_dict(self):
        self.pre_process_model()
        self.train_model()

        for record in self.final.to_dict(orient="records"):
            rou = round(record['prediction'], 2)
            if rou < record['invoice_amount_doc_currency']:
                self.mapped_result[record['pk_id']] = {'amount': rou, 'type': "Partially Paid"}
            else:
                self.mapped_result[record['pk_id']] = \
                    {'amount': record['invoice_amount_doc_currency'], 'type': "Fully Paid"}

    def get_prediction_of_pk_id(self, number):
        try:
            return self.mapped_result[number]
        except KeyError:
            return {'amount': -1, 'type': '-'}


if __name__ == '__main__':
    pay = PaymentPredictor()
    pay.load_data_from_db("project")
    pay.prepare_dict()
