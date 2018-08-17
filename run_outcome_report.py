import datetime
import pandas as pd

from features.data_provider import all_features, other_features, player_features, DataLoader
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

    params = get_default_parameters()
    arguments = get_cv_grid_search_arguments(params, X)
    results = run_grid_search_for_outcome(arguments, X, y)
    results.to_csv(f"outcome_hyperparam_optimization_{name}.csv")
    best_params_dict = get_best_params(results)
    write_log(file_name, str(best_params_dict), print_text=True)

    optimal_params = params.copy()
    optimal_params["max_depth"] = best_params_dict["max_depth"]
    optimal_params["min_samples_leaf"] = best_params_dict["min_samples_leaf"]
    optimal_params["max_features"] = best_params_dict["max_features"]

    for (tt_file, bet_file, filter_start) in tournament_parameters:
        data_loader.set_filter_start(filter_start)
        simulations, units, kellys = iterate_simulations(data_loader,
                                                         tt_file,
                                                         bet_file,
                                                         run_outcome_model_for_features,
                                                         optimal_params)
        report = simulation_iteration_report(simulations, units, kellys)
        report["id"] = f"{name}_{filter_start}"
        report["max_depth"] = optimal_params["max_depth"]
        report["min_samples_leaf"] = optimal_params["min_samples_leaf"]
        report["max_features"] = optimal_params["max_features"]

        write_log(file_name, str(report), print_text=True)
        reports.append(report)

pd.DataFrame(reports).to_csv("outcome_model_report.csv")
