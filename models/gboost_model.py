from sklearn.ensemble import GradientBoostingClassifier

def get_model(params=None, X=None, y=None):
    if not params:
        params = {
            'learning_rate': 0.01,
            'max_depth': 5,
            'max_features': 'sqrt',
            'min_samples_leaf': 10,
            'n_estimators': 250
        }
    model = GradientBoostingClassifier(**params)
    if (X is not None) and (y is not None):
        model.fit(X, y)

    print(params)
    return model
