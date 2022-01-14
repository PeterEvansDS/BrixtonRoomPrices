import pandas as pd
from config import BINARY_COLS, ONE_HOT_COLS, ORDINAL_COLS

def binary_encode(X, col):
    one_value = BINARY_COLS[col][0]
    zero_value = BINARY_COLS[col][1]
    return X.replace({one_value:int(1), zero_value:int(0)})

def ordinal_encode(X, col):
    values = ORDINAL_COLS[col]
    ordinal_dict = {k: v for v, k in enumerate(values)}
    return X.replace(ordinal_dict)

def one_hot_encode(X):
    return pd.get_dummies(X, dummy_na = True, drop_first = True)
