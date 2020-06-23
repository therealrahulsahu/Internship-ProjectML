import mysql.connector as cnn
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


class _1705157:
    def __init__(self):
        self.train = pd.DataFrame([])
        self.mean_cs_no = {}

        self.load_data_from_db("project")
        self.pre_process_model()
        self.model_train()

    def load_data_from_db(self, database, host="localhost", user="root", password="root"):
        try:
            my_db = cnn.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            my_cs = my_db.cursor()

            train_columns = ["customer_number", "cust_payment_terms", "total_open_amount",
                             "paid_amount", "clearing_date", "invoice_id"]
            train_query = "select customer_number, cust_payment_terms, total_open_amount, paid_amount," \
                          " clearing_date, invoice_id from customer_invoice where clearing_date is not null order" \
                          " by clearing_date;"
            my_cs.execute(train_query)
            train_tuples = list(my_cs.fetchall())

            self.train = pd.DataFrame(train_tuples, columns=train_columns)

            my_db.close()
            my_cs.close()
        except Exception as e:
            print(e)

    def pre_process_model(self):
        self.train = self.train.drop_duplicates(subset='invoice_id', keep='first')

        coded_mean = self.train.groupby('customer_number').mean().paid_amount

        self.mean_cs_no = coded_mean.to_dict()
        self.train['mean_code'] = self.train.customer_number.map(coded_mean)

    def model_train(self):
        x_train = self.train[["mean_code", "cust_payment_terms"]]
        y_train = self.train[['paid_amount']]

        # SVR
        self.sc = StandardScaler()
        x_sc_train = self.sc.fit_transform(x_train)
        y_sc_train = self.sc.fit_transform(y_train)

        # Fitting SVR to the dataset
        self.reg = SVR(kernel='rbf')
        self.reg.fit(x_sc_train, y_sc_train)

    def get_prediction_from_values(self, customer_no, cust_pay_terms, actual_amount):
        try:
            test_data = [[self.mean_cs_no[customer_no], cust_pay_terms],
                         [self.mean_cs_no[228442], 60]]
            sc_trans = self.sc.fit_transform(test_data)
            sc_pred = self.reg.predict(sc_trans)
            pred = self.sc.inverse_transform(sc_pred)
            if pred[0] < actual_amount:
                return {'amount': round(pred[0], 2), 'type': 'Partially Paid'}
            else:
                return {'amount': round(actual_amount, 2), 'type': 'Fully Paid'}
        except KeyError:
            return {'amount': -1, 'type': 'Customer Not Found'}

    def getPredictions(self, data):
        try:
            result = []
            for query in data:
                result.append(
                    self.get_prediction_from_values(
                        query['customer_number'],
                        query['cust_payment_terms'],
                        query['actual_open_amount'])
                )
            return result
        except KeyError:
            return [{'amount': -1, 'type': 'Invalid arguments'}]
