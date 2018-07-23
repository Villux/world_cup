import numpy as np

def get_best_params(results, verbose=False):
    results["best_combo"] = results["test_acc"] + results["wc_acc"]
    best_params = results.loc[results['best_combo'].idxmax(), ["max_depth", "max_features", "min_samples_leaf"]]
    if verbose:
        columns = ["max_depth", "max_features", "min_samples_leaf", "test_acc", "wc_acc"]
        print("Test set bests")
        print(results.loc[results['test_acc'].idxmax(), columns])
        print(results.loc[results['test_mae'].idxmin(), columns])
        print(results.loc[results['test_mse'].idxmin(), columns])
        print()
        print("WC set bests")
        print(results.loc[results['wc_acc'].idxmax(), columns])
        print(results.loc[results['wc_mae'].idxmin(), columns])
        print(results.loc[results['wc_mse'].idxmin(), columns])
        print()
        print("BEST COMBO")
        print(best_params)
     
    best_params = best_params.replace({np.nan:None})
    return best_params.to_dict()

def get_feature_importance(feature_importances, feature_columns):
    zipped = sorted(zip(feature_columns, feature_importances), key = lambda t: t[1], reverse=True)
    D = {}
    for feature, importance in zipped:
        D[feature] = round(importance, 5)
    return D

