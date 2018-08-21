import datetime
import pandas as pd

from features.data_provider import all_features, other_features, player_features, DataLoader
from notebook_helpers import iterate_simulations, run_gboost_model_for_features, simulation_iteration_report
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import make_scorer, accuracy_score, log_loss

def write_log(filename, text, print_text=False):
    with open(filename, "a") as f:
        f.write(text + "\n")

    if print_text:
        print(text)

def get_optimal_params():

    param_grid = {
        'learning_rate':[0.1,0.01],
        'n_estimators':[100,250],
        'max_features': ["sqrt", "log2"],
        'max_depth': [3, 5, 8, 12, None],
        'min_samples_leaf': [1, 3, 5, 10, 15]
    }

    scoring = {'Accuracy': make_scorer(accuracy_score), "LogLoss": make_scorer(log_loss)}
    tuning = GridSearchCV(
        estimator=GradientBoostingClassifier(random_state=10),
        param_grid = param_grid,
        scoring=scoring,
        n_jobs=12,
        cv=5)
    tuning.fit(X, y)
    return tuning.best_params_

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

    optimal_params = get_optimal_params()
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
