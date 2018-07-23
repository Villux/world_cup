from time import time
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

def run_custom_grid_search(org_params, Xtrain, ytrain, Xtest, ytest, X_wc, y_wc, classifier=True):
    start = time()

    results = []
    params = org_params.copy()

    i = 0
    for depth in [3, 5, 8, 12, None]:
        for min_samples in [1, 3, 5, 10, 15]:
            for max_features in ["sqrt", "log2"]:
                    params["max_depth"] = depth
                    params["min_samples_leaf"] = min_samples
                    params["max_features"] = max_features

                    if classifier:
                        model = RandomForestClassifier(**params)
                    else:
                        model = RandomForestRegressor(**params)
                    model.fit(Xtrain, ytrain)

                    res = {
                        "max_depth": depth,
                        "min_samples_leaf": min_samples,
                        "max_features": max_features,
                    }

                    y_true, y_pred = ytrain, model.predict(Xtrain)
                    res["train_acc"] = sum(np.around(y_pred) == y_true) / len(Xtrain)
                    res["train_mae"] = mean_absolute_error(y_true, y_pred)
                    res["train_mse"] = mean_squared_error(y_true, y_pred)

                    y_true, y_pred = ytest, model.predict(Xtest)
                    res["test_acc"] = sum(np.around(y_pred) == y_true) / len(Xtest)
                    res["test_mae"] = mean_absolute_error(y_true, y_pred)
                    res["test_mse"] = mean_squared_error(y_true, y_pred)

                    y_true, y_pred = y_wc, model.predict(X_wc)
                    res["wc_acc"] = sum(np.around(y_pred) == y_true) / len(X_wc)
                    res["wc_mae"] = mean_absolute_error(y_true, y_pred)
                    res["wc_mse"] = mean_squared_error(y_true, y_pred)

                    results.append(res)
                    i += 1

    print("Parameter estimation took: ", time() - start)
    return pd.DataFrame(results)
