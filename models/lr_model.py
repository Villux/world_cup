from sklearn.linear_model import LogisticRegression

def get_model(params=None, X=None, y=None):
    if not params:
        params = {'n_jobs': 1, "solver": "newton-cg"}
    model = LogisticRegression(**params)
    if (X is not None) and (y is not None):
        model.fit(X, y)

    return model
