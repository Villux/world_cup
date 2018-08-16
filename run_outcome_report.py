import datetime
import pandas as pd

from features.data_provider import set_feature_columns, player_features
from features.data_provider import feature_columns, other_features, get_whole_dataset
from models.helpers import get_default_parameters
from notebook_helpers import run_grid_search_for_outcome, get_cv_grid_search_arguments
from notebook_helpers import iterate_simulations, run_outcome_model_for_features, simulation_iteration_report

def write_log(filename, text, print_text=False):
    with open(filename, "a") as f:
        f.write(text + "\n")

    if print_text:
        print(text)

tournament_parameters = [
    ('data/original/wc_2018_games_real.csv', 'data/original/wc_2018_bets.csv', "2018-06-14"),
    ('data/original/wc_2014_games_real.csv', 'data/original/wc_2014_bets.csv', "2014-06-12"),
    ('data/original/wc_2010_games_real.csv', 'data/original/wc_2010_bets.csv', "2010-06-11")
]
feature_sets = [
    ("all_features", feature_columns),
    ("general_features", other_features),
    ("player_features", player_features)
]

file_name = "outcome_report_full.txt"

reports = []
for (name, feature_set) in feature_sets:
    write_log(file_name, str(datetime.datetime.now()))
    write_log(file_name, f"Running test for feature set: {name}", print_text=True)

    set_feature_columns(feature_set)
    X, y = get_whole_dataset("home_win")

    params = get_default_parameters()
    arguments = get_cv_grid_search_arguments(params, X)
    results = run_grid_search_for_outcome(arguments, X, y)
    results.to_csv(f"outcome_hyperparam_optimization_{name}.csv")
    best_params = results.sort_values(['test_acc', 'test_logloss'], ascending=[False, True]).iloc[0]
    best_params_dict = best_params.to_dict()
    write_log(file_name, best_params_dict)

    optimal_params = params.copy()
    optimal_params["max_depth"] = best_params_dict["max_depth"]
    optimal_params["min_samples_leaf"] = best_params_dict["min_samples_leaf"]
    optimal_params["max_features"] = best_params_dict["max_features"]

    for (tt_file, bet_file, filter_start) in tournament_parameters:
        simulations, units, kellys = iterate_simulations(feature_set,
                                                         tt_file,
                                                         bet_file,
                                                         run_outcome_model_for_features,
                                                         filter_start=filter_start,
                                                         params=optimal_params)
        report = simulation_iteration_report(simulations, units, kellys)

        write_log(file_name, report, print_text=True)
        reports.append(report)

pd.DataFrame(reports).to_csv("outcome_model_report.csv")
