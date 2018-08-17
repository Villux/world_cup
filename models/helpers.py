import numpy as np

def get_best_params(results):
    best_params = results.sort_values(['test_acc', 'test_logloss'], ascending=[False, True]).iloc[0]
    best_params = best_params.replace({np.nan:None})
    return best_params.to_dict()

def get_feature_importance(feature_importances, feature_columns):
    zipped = sorted(zip(feature_columns, feature_importances), key = lambda t: t[1], reverse=True)
    D = {}
    for feature, importance in zipped:
        D[feature] = round(importance, 5)
    return D

def get_default_parameters():
    return {"oob_score":True, "bootstrap":True, "n_jobs":-1, "n_estimators": 2000}

