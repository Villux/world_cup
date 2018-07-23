from sklearn.ensemble import RandomForestClassifier

def get_model(params=None, X=None, y=None):
    if not params:
        params = {
            'oob_score' : True,
            'bootstrap': True,
            'n_jobs':-1,
            'n_estimators': 200,
            "max_depth": 5,
            "min_samples_leaf": 1,
            "max_features": "log2"
        }
    model = RandomForestClassifier(**params)
    if (X is not None) and (y is not None):
        model.fit(X, y)

    return model
