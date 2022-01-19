from sklearn import linear_model
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor


HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1'}
INFO_BOX_XPATH = '//*[@id="spareroom"]/div[2]/div/div/div[2]/div/div[2]/div[2]/'
SEARCH_URL = 'https://www.spareroom.co.uk/flatshare/index.cgi?&search_id=' + SEARCH_ID + '&offset=0&sort_by='
BASE_URL = 'https://www.spareroom.co.uk'

BINARY_COLS = {'balcony': ['Yes', 'No'],
               'ensuite': [True, False],
               'broadband': ['Yes', 'No'],
               'disabled_access': ['Yes', 'No'],
               'furnished': ['Furnished', 'Unfurnished'],
               'living_room': ['shared', 'No'],
               'mon-fri': ['Yes', 'No'],
               'house_type': ['House share', 'Flat share'],
               'parking': ['Yes', 'No'],
               'double' : ['double', 'single'],
               'walk_to_station': ['walk', 'bus']
               }

ONE_HOT_COLS = ['area', 'gender', 'postcode']

ORDINAL_COLS = {'bills': ['No', 'Some', 'Yes']}

GRID_PARAMS = [
        {'model': [linear_model.Ridge()],
        'model__alpha':[x/10 for x in range(5, 50)]},
        {'model':[linear_model.Lasso()],
        'model__alpha':[x/10 for x in range(1, 50)]},
        {'model':[DecisionTreeRegressor()],
        'model__ccp_alpha':[x/10 for x in range(0, 10)]},
        {'model':[RandomForestRegressor()],
        'model__n_estimators':[10, 100, 200],
        'model__max_features':[2,5,10]}
]
