from sklearn.ensemble import RandomForestRegressor

def get_model(params=None, X=None, y=None):
    if not params:
        params = {
            'oob_score' : True,
            'bootstrap': True,
            'n_jobs':-1,
            'n_estimators': 1000,
            "max_depth": None,
            "min_samples_leaf": 5,
            "max_features": "sqrt"
        }
    model = RandomForestRegressor(**params)
    if X and y:
        model.fit(X, y)

    return model
