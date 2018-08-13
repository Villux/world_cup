from sklearn.ensemble import RandomForestRegressor

def get_model(params=None, X=None, y=None, n_estimators=200):
    if not params:
        params = {
            'oob_score' : True,
            'bootstrap': True,
            'n_jobs':-1,
            'n_estimators': n_estimators,
            "max_depth": 8,
            "min_samples_leaf": 5,
            "max_features": "log2"
        }
    model = RandomForestRegressor(**params)
    if (X is not None) and (y is not None):
        model.fit(X, y)

    print(params)
    return model
