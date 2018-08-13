from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV

def get_model(params, name, calibration=None, X=None, y=None):
    base_model = RandomForestClassifier(**params)
    if not calibration:
        model = base_model
    else:
        model = CalibratedClassifierCV(base_model, cv=10, method=calibration)

    if (X is not None) and (y is not None):
        model.fit(X, y)

    print(f"Model type: {name}, model calibration: {'None' if not calibration else calibration}, parameters: {params}")
    return model

def get_home(params=None, calibration=None, X=None, y=None, n_estimators=200):
    if not params:
        params = {
            'oob_score' : True,
            'bootstrap': True,
            'n_jobs':-1,
            'n_estimators': n_estimators,
            "max_depth": None,
            "min_samples_leaf": 15,
            "max_features": "sqrt"
            }
    return get_model(params, "Home", calibration=calibration, X=X, y=y)

def get_draw(params=None, calibration=None, X=None, y=None, n_estimators=200):
    if not params:
        params = {
            'oob_score' : True,
            'bootstrap': True,
            'n_jobs':-1,
            'n_estimators': n_estimators,
            "max_depth": 5,
            "min_samples_leaf": 15,
            "max_features": "sqrt"
        }
    return get_model(params, "Draw", calibration=calibration, X=X, y=y)


def get_away(params=None, calibration=None, X=None, y=None, n_estimators=200):
    if not params:
        params = {
            'oob_score' : True,
            'bootstrap': True,
            'n_jobs':-1,
            'n_estimators': n_estimators,
            "max_depth": 8,
            "min_samples_leaf": 10,
            "max_features": "sqrt"
        }
    return get_model(params, "Away", calibration=calibration, X=X, y=y)
