import pandas as pd
import string
from decimal import Decimal
from sklearn.base import BaseEstimator, TransformerMixin

class DataFrameTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, na_impute = False):
        self.na_impute = na_impute
        self.binary_cols = [('balcony', 'Yes', 'No'),
                            ('broadband', 'Yes', 'No'),
                            ('disabled_access', 'Yes', 'No'),
                            ('furnished', 'Furnished', 'Unfurnished'),
                            ('living_room', 'shared', 'No'),
                            ('house_type', 'House share', 'Flat share'),
                            ('parking', 'Yes', 'No'),
                            ('double', 'double', 'single'),
                            ('walk_to_station', 'walk', 'bus')]
        self.one_hot_cols = ['area', 'gender', 'postcode', ]
        self.ordinal_cols = [('bills', ['No', 'Some', 'Yes'])]

    def remove_non_rooms(self, X):
        X = X[~X.house_type.str.contains('rent')]
        return X

    def extract_price_data(self, X):
        """Extracts the different data found in the original 'price' tag. """

        X.price = X.price.apply(lambda x: x.replace('£', '').replace(',',''))
        price = X.price.apply(lambda x: int(x.split(' ')[0]))
        rate = X.price.apply(lambda x: x.split(' ')[1])
        ensuite = X.price.str.contains('en suite', regex=False)

        try:
            type = X.price.apply(lambda x: ' '.join(x.split(' ')[2:]).strip('()'))
        except:
            type = None
        type = type.map(lambda x: x.replace('/en suite', ''))

        df = pd.DataFrame({'price':price, 'price_rate':rate, 'double':type, 'ensuite':ensuite})

        X = X.drop('price', axis = 1)
        X = X.join(df)
        return X

    def price_converter(self, X):
        price_pcm = X.apply(lambda x: x['price'] if x['price_rate'] == 'pcm' else x['price']*52/12, axis = 1)
        X = X.drop('price_rate', axis = 1)
        X = X.assign(price = price_pcm)
        return X

    def availability_from_now(self, X):
        availability = X.available_in.map(lambda x: (pd.to_datetime('now') if x == 'Now'
                                                else pd.to_datetime(x) ) - pd.to_datetime('now'))
        X['available_in'] = availability.round('D')
        return X

    def term_transformer(self, X):
        max_term = X.max_term.map(lambda x: 0 if x == 'None' else 1)
        min_term = X.min_term.map(lambda x: 0 if x == 'None' else int(x.split()[0]))
        X['max_term'] = max_term
        X['min_term'] = min_term
        return X

    def extract_ad_ref(self, X):
        ad_ref = X.ad_ref
        X['mon_fri'] = ad_ref.str.contains('Mon-Fri')
        X = X.assign(ad_ref = ad_ref.str.extract('(\d+)'))
        return X

    def extract_postcode(self, X):
        X.postcode = X.postcode.map(lambda x: x.split()[0])
        return X

    def transform_deposit(self, X):
        deposit = X.deposit.str.replace('£', '').str.replace(',','')
        deposit = deposit.astype('float')
        X = X.assign(deposit = deposit)
        return X

    def extract_time_to_station(self, X):

        df = pd.DataFrame({
        'distance_to_station' : X.distance_to_station.map(lambda x: x.split('-')[0], na_action = 'ignore'),
        'walk_to_station' : X.distance_to_station.map(lambda x: x.split(' ')[-2], na_action = 'ignore')
        })

        X = X.drop('distance_to_station', axis = 1)
        X = X.join(df)
        return X

    def binary_encode(self, X, col, one_value, zero_value):
        X[col] = X[col].replace({one_value:int(1), zero_value:int(0)})
        return X

    def ordinal_encode(self, X, col, values):
        ordinal_dict = {k: v for v, k in enumerate(values)}
        X[col] = X[col].replace(ordinal_dict)
        return X

    def encode_columns(self, X, binary_cols, one_hot_cols, ordinal_cols):
        if self.na_impute == False:
            dummy_na = True
        else:
            dummy_na = False


        for col in binary_cols:
            X = self.binary_encode(X, col[0], col[1], col[2])

        for col in ordinal_cols:
            X = self.ordinal_encode(X, col[0], col[1])

        X = pd.get_dummies(X, columns = one_hot_cols, dummy_na = dummy_na, drop_first = True)
        return X

    def null_handler(self, X, na_impute):
        if na_impute == False:
            X = X.dropna(axis = 0, how = 'any')
        else:
            X = X
        return X

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = self.remove_non_rooms(X)
        X = self.extract_price_data(X)
        X = self.price_converter(X)
        X = self.availability_from_now(X)
        X = self.extract_ad_ref(X)
        X = self.extract_postcode(X)
        X = self.transform_deposit(X)
        X = self.term_transformer(X)
        X = self.extract_time_to_station(X)
        X = self.encode_columns(X, self.binary_cols, self.one_hot_cols, self.ordinal_cols)
        # X = self.null_handler(X, self.na_impute)

        return X
