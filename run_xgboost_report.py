import datetime
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import KFold

from features.data_provider import all_features, other_features, player_features, DataLoader
from notebook_helpers import iterate_simulations, run_gboost_model_for_features, simulation_iteration_report
from models.helpers import get_default_parameters, get_best_params


def write_log(filename, text, print_text=False):
    with open(filename, "a") as f:
        f.write(text + "\n")

    if print_text:
        print(text)

def get_grid_search_arguments(X):
    kf_splits = 5
    kf = KFold(n_splits=kf_splits)
    arguments = []

    org_params = {'n_estimators': 250}

    for lr in [0.1, 0.01]:
        for mf in ["sqrt", "log2"]:
            for md in [3, 5, 8, 12]:
                for msl in [1, 3, 5, 10, 15]:
                    params = org_params.copy()
                    params["learning_rate"] = lr
                    params["max_depth"] = md
                    params["min_samples_leaf"] = msl
                    params["max_features"] = mf
                    arg_array = []
                    for train_index, test_index in kf.split(X):
                        arg_array.append((params, train_index, test_index))
                    arguments.append(arg_array)

    return arguments

def get_model_metrics(args):
    params = args[0]
    Xtrain, ytrain = args[1], args[2]
    Xtest, ytest = args[3], args[4]
    model = GradientBoostingClassifier(**params)
    model.fit(Xtrain, ytrain)
    y_true, y_pred = ytest, model.predict(Xtest)
    y_pred_prob = model.predict_proba(Xtest)

    return accuracy_score(y_true, y_pred), log_loss(y_true, y_pred_prob)

def run_grid_search(arguments, X, y):
    metrics = []
    pool = Pool(cpu_count())
    for cv_args in arguments:
        args = []
        cv_params = {}
        for (params, train_index, test_index) in cv_args:
            args.append((params, X.iloc[train_index], y.iloc[train_index], X.iloc[test_index], y.iloc[test_index]))
            cv_params = params
        results = pool.map(get_model_metrics, args)
        metrics.append({
            'learning_rate': cv_params["learning_rate"],
            "max_depth": cv_params["max_depth"],
            "min_samples_leaf": cv_params["min_samples_leaf"],
            "max_features": cv_params["max_features"],
            "test_acc": np.mean([result[0] for result in results]),
            "test_logloss": np.mean([result[1] for result in results])
        })
    return pd.DataFrame(metrics)

tournament_parameters = [
    ('data/original/wc_2018_games_real.csv', 'data/original/wc_2018_bets.csv', "2018-06-14"),
    ('data/original/wc_2014_games_real.csv', 'data/original/wc_2014_bets.csv', "2014-06-12"),
    ('data/original/wc_2010_games_real.csv', 'data/original/wc_2010_bets.csv', "2010-06-11")
]
feature_sets = [
    ("all_features", all_features),
    ("general_features", other_features),
    ("player_features", player_features)
]

file_name = "outcome_report_full.txt"

reports = []
for (name, feature_set) in feature_sets:
    write_log(file_name, str(datetime.datetime.now()))
    write_log(file_name, f"Running test for feature set: {name}", print_text=True)

    data_loader = DataLoader(feature_set)
    X, y = data_loader.get_all_data("home_win")

    arguments = get_grid_search_arguments(X)
    results = run_grid_search(arguments, X, y)
    results.to_csv(f"gboost_hyperparam_optimization_{name}.csv")
    best_params_dict = get_best_params(results)
    optimal_params = {'n_estimators': 250}
    optimal_params["learning_rate"] = best_params_dict["learning_rate"]
    optimal_params["max_depth"] = best_params_dict["max_depth"]
    optimal_params["min_samples_leaf"] = best_params_dict["min_samples_leaf"]
    optimal_params["max_features"] = best_params_dict["max_features"]

    write_log(file_name, str(optimal_params), print_text=True)

    for (tt_file, bet_file, filter_start) in tournament_parameters:
        data_loader.set_filter_start(filter_start)
        simulations, units, kellys = iterate_simulations(data_loader,
                                                         tt_file,
                                                         bet_file,
                                                         run_gboost_model_for_features,
                                                         optimal_params)
        report = simulation_iteration_report(simulations, units, kellys)
        report["id"] = f"{name}_{filter_start}"
        report["max_depth"] = optimal_params["max_depth"]
        report["min_samples_leaf"] = optimal_params["min_samples_leaf"]
        report["max_features"] = optimal_params["max_features"]
        report["learning_rate"] = optimal_params["learning_rate"]
        report["n_estimators"] = optimal_params["n_estimators"]

        write_log(file_name, str(report), print_text=True)
        reports.append(report)

pd.DataFrame(reports).to_csv("gboost_outcome_model_report.csv")
