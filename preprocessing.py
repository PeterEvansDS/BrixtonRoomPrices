import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
import string
from config import BINARY_COLS, ONE_HOT_COLS, ORDINAL_COLS
from encoders import binary_encode, ordinal_encode, one_hot_encode

#transformers are written in classes that can be used within an sklearn pipeline

class PropertyRemover(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[~X.house_type.str.contains('rent')]

class PriceExtractor(BaseEstimator, TransformerMixin):

    """ Extract all pieces of information present in the price html tag. """

    def extract_data(self, X):
        price = X.price.apply(lambda x: x.replace('£', '').replace(',',''))
        price = price.apply(lambda x: int(x.split(' ')[0]))
        rate = X.price.apply(lambda x: x.split(' ')[1])
        ensuite = X.price.str.contains('en suite', regex=False)

        try:
            type = X.price.apply(lambda x: ' '.join(x.split(' ')[2:]).strip('()'))
        except:
            type = None
        type = type.map(lambda x: x.replace('/en suite', ''))

        return pd.DataFrame({'price':price, 'price_rate':rate, 'double':binary_encode(type, 'double'), 'ensuite':binary_encode(ensuite, 'ensuite')})

    def convert_price(self, df):
        price_pcm = df.apply(lambda x: x['price'] if x['price_rate'] == 'pcm' else x['price']*52/12, axis = 1)
        df = df.drop('price_rate', axis = 1)
        df = df.assign(price = price_pcm)
        return df

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return self.convert_price(self.extract_data(X))

class AvailabilityTransformer(BaseEstimator, TransformerMixin):

    def fit (self, X, y=None):
        return self

    def transform(self, X):
        availability = X['available_in'].map(lambda x: (pd.to_datetime('now') if x == 'Now'
                                                else pd.to_datetime(x) ) - pd.to_datetime('now'))
        availability = availability.dt.days.map(lambda x: 0 if (x < 0) else x)
        return pd.DataFrame({'available_in':availability})

class TermTransformer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return pd.DataFrame({
        'max_term':X.max_term.map(lambda x: 0 if x == 'None' else 1),
        'min_term': X.min_term.map(lambda x: 0 if x == 'None' else int(x.split()[0]))
        })

class AdRefExtractor(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):

        ad_ref = X.ad_ref.str.extract('(\d+)').iloc[:, 0]
        mon_fri = X.ad_ref.str.contains('Mon-Fri')

        return pd.DataFrame({'ad_ref':ad_ref, 'mon_fri':binary_encode(mon_fri, 'mon-fri')})

class PostcodeExtractor(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return pd.DataFrame({'postcode':X.postcode.map(lambda x: x.split()[0])})

class DepositTransformer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = pd.DataFrame({
        'deposit':X.deposit.str.replace('£', '').str.replace(',','').astype(float)
        })
        return df

class TimeToStationExtractor(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        distance_to_station = X.distance_to_station.map(lambda x: x.split('-')[0], na_action = 'ignore')
        walk_to_station = X.distance_to_station.map(lambda x: x.split(' ')[-2], na_action = 'ignore')
        walk_to_station = walk_to_station.map(lambda x: None if x not in ['walk', 'bus'] else x)
        return pd.DataFrame({
            'distance_to_station' : distance_to_station,
            'walk_to_station' : binary_encode(walk_to_station, 'walk_to_station')
            })

class BinaryEncoder(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = pd.DataFrame()
        for col in X.columns:
            df[col] = binary_encode(X[col], col)
        return df

class OrdinalEncoder(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = pd.DataFrame()
        for col in X.columns:
            df[col] = ordinal_encode(X[col], col)
        return df

class OneHotEncoder(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return one_hot_encode(X)


class Imputer(BaseEstimator, TransformerMixin):

    def __init__(self, na_impute = False):
        self.na_impute = False

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if self.na_impute == True:
            return SimpleImputer(strategy='median').fit_transform(X)
        else:
            return pd.DataFrame(X).dropna()
