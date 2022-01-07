import pandas as pd
import string
from decimal import Decimal
from sklearn.base import BaseEstimator, TransformerMixin

class DataCleaner(BaseEstimator, TransformerMixin):

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

        df = pd.DataFrame({'price':price, 'price_rate':rate, 'room_type':type, 'ensuite':ensuite})

        X = X.drop('price', axis = 1)
        X = X.join(df)
        return X

    def availability_from_now(self, X):
        availability = X.available_in.map(lambda x: (pd.to_datetime('now') if x == 'Now'
                                                else pd.to_datetime(x) ) - pd.to_datetime('now'))
        X['available_in'] = availability.round('D')
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
        'to_station_transport' : X.distance_to_station.map(lambda x: x.split(' ')[-2], na_action = 'ignore')
        })

        X = X.drop('distance_to_station', axis = 1)
        X = X.join(df)
        return X

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = self.remove_non_rooms(X)
        X = self.extract_price_data(X)
        X = self.availability_from_now(X)
        X = self.extract_ad_ref(X)
        X = self.extract_postcode(X)
        X = self.transform_deposit(X)
        X = self.extract_time_to_station(X)
        return X
