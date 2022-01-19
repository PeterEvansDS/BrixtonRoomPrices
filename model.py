import pandas as pd
import numpy as np
import joblib

from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV

from config import GRID_PARAMS
from preprocessing import (PropertyRemover, PriceExtractor, AvailabilityTransformer,
                           TermTransformer, AdRefExtractor, PostcodeExtractor,
                           DepositTransformer, TimeToStationExtractor, BinaryEncoder,
                           OrdinalEncoder, OneHotEncoder, Imputer, prep_for_model)

class DummyEstimator(BaseEstimator):
    #class is used to enable the testing of different regression algorithms in the model with GridSearchCV
    def fit(self): pass
    def score(self): pass

def build_model():

    column_transformer = ColumnTransformer([
        ('available_in', AvailabilityTransformer(), ['available_in']),
        ('lease_terms', TermTransformer(), ['max_term', 'min_term']),
        ('ad_ref', AdRefExtractor(), ['ad_ref']),
        ('deposit', DepositTransformer(), ['deposit']),
        ('time_to_station', TimeToStationExtractor(), ['distance_to_station']),
        ('binary_encode', BinaryEncoder(), ['balcony', 'broadband', 'disabled_access', 'living_room',
                                            'furnished', 'house_type', 'parking']),
        ('ordinal_encode', OrdinalEncoder(), ['bills']),
        ('one_hot', OneHotEncoder(), ['postcode', 'gender'])
    ], remainder = 'drop')

    # null_imputer = Pipeline([('imputer', Imputer(na_impute=na_impute))])
    null_imputer = Pipeline([('imputer', SimpleImputer(strategy='median'))])


    model = Pipeline([('transformer', column_transformer),
                      ('null_imputer', null_imputer),
                      ('model', DummyEstimator())])

    return model

def tune_model(df):

    X_train, X_test, y_train, y_test = prep_for_model(df)

    model = build_model()
    gs = GridSearchCV(model, GRID_PARAMS, scoring='r2', n_jobs=-1, cv=3)
    gs.fit(X_train, y_train)

    print("Best Hyperparameters: {}".format(gs.best_params_))
    print("Best score: {}".format(gs.best_score_))

    return


def train_model(df, model_name, params, print_params=False):
    X_train, X_test, y_train, y_test = prep_for_model(df)

    model = build_model()
    model.set_params(**params)

    if print_params:
        print(model.get_params())

    model.fit(X_train, y_train)

    joblib.dump(model, model_name)
    return


def test_model(df, model_name):
    X_train, X_test, y_train, y_test = prep_for_model(df)
    model = joblib.load(model_name)

    y_pred = model.predict(X_test)

    print("R2 on the test set: {}".format(r2_score(y_test, y_pred)))
    return
