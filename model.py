import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from preprocessing import PropertyRemover, PriceExtractor, AvailabilityTransformer, TermTransformer, AdRefExtractor, PostcodeExtractor, DepositTransformer, TimeToStationExtractor, BinaryEncoder, OrdinalEncoder, OneHotEncoder, Imputer
from config import BINARY_COLS, ONE_HOT_COLS, ORDINAL_COLS

def build_model():

    invalid_remover = Pipeline([('remover', PropertyRemover())])
    column_transformer = ColumnTransformer([
        ('price', PriceExtractor(), ['price']),
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

    null_imputer = Imputer(na_impute=True)

    preprocessor = Pipeline([('remover', invalid_remover),
                      ('transformer', column_transformer),
                      ('null_imputer', null_imputer)])

    return preprocessor
