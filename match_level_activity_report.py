import pickle
import json
import argparse
from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt

from features.data_provider import other_features, all_features, player_features, DataLoader
from notebook_helpers import run_score_model_for_features
from models.helpers import get_feature_importance, get_default_parameters
from country_list import get_country_code

figsize = (12, 6)

parser = argparse.ArgumentParser()
parser.add_argument('-y', type=int, default=2014, help="Which year's World cup")
parser.add_argument('-f', type=str, help="Filename prefix")
args = parser.parse_args()

def write_as_pickle(data, filename):
    with open(f'img/meta/{filename}.pickle', 'wb') as outfile:
        pickle.dump(data, outfile)

def write_as_json(data, filename):
    with open(f'{filename}.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def get_cum_return(strategy):
    initial_capital = strategy.initial_capital
    net_returns = np.array(strategy.get_returns())
    returns = net_returns + 1
    returns[0] *= initial_capital
    return np.cumprod(returns)

def plot_cum_returns(strategies, filename, xtick_labels):
    plt.subplots(figsize=figsize)
    for (strategy, label_name) in strategies:
        cum_return = get_cum_return(strategy)
        plt.plot(cum_return, label=label_name)

    plt.xticks(np.arange(0, len(cum_return)), xtick_labels)
    plt.xticks(rotation='vertical', fontsize=8)
    plt.ylabel('Cash balance')
    plt.legend()
    plt.savefig(f"img/{filename}.eps")

def plot_bet_sizes(strategies, filename, xtick_labels):
    plt.subplots(figsize=figsize)
    width = 0.25
    for ind, (strategy, label_name) in enumerate(strategies):
        fractions = strategy.get_fractions()
        index = np.arange(0, len(fractions))
        plt.bar(index + (ind * width), fractions, width, label=label_name)

    plt.xticks(index + width, xtick_labels)
    plt.xticks(rotation='vertical', fontsize=8)
    plt.ylabel('Bet size fraction')
    plt.legend()
    plt.savefig(f"img/{filename}.eps")

def plot_probabilities(simulations, filename, xtick_labels):
    keys = ["home_win_prob", "draw_prob", "away_win_prob"]
    js_dict = {}
    for key in keys:
        plt.figure(figsize=figsize)
        for (simulation, label_name) in simulations:
            plt.plot(simulation[key].values, label=label_name)
            plt.xticks(np.arange(0, len(simulation[key].values)), xtick_labels)
        plt.legend()
        plt.ylim(0, 1)
        plt.ylabel('Probability')
        plt.xticks(rotation='vertical', fontsize=8)
        plt.savefig(f'img/{filename}_{key}.eps')

        probabilities = [simulation[key].values for (simulation,_) in simulations]
        avg_probs = [np.mean(p) for p in probabilities]
        stds = [np.std(p) for p in probabilities]
        N = len(probabilities)
        correlation_matrix = np.ones((N, N))
        for (x, y), (col_idx, row_idx) in zip(combinations(probabilities, r=2), combinations(np.arange(N), r=2)):
            corr_coef = np.corrcoef(x, y)
            correlation_matrix[row_idx, col_idx] = corr_coef[1, 0]

        tmp = {}
        tmp["probabilities"] = avg_probs
        tmp["std"] = stds
        tmp["correlation_matrix"] = correlation_matrix.tolist()

        js_dict[key] = tmp

    with open(f"img/meta/{filename}", "w") as text_file:
        text_file.write(json.dumps(js_dict, indent=2))



def simulate(tournament_template_file, match_bet_file, data_loader, params, filename):
    (simulation, unit, kelly), model = run_score_model_for_features(data_loader, tournament_template_file, match_bet_file, params)
    feat_impor = get_feature_importance(model.feature_importances_, data_loader.feature_columns)

    tmp = {
        "unit": unit,
        "kelly": kelly,
        "simulation": simulation,
        "feature_importance": feat_impor
    }
    write_as_pickle(tmp, filename)
    return tmp

if __name__ == "__main__":
    if args.y == 2010:
        tt_file = 'data/original/wc_2010_games_real.csv'
        mb_file = 'data/original/wc_2010_bets.csv'
        filter_start = "2010-06-11"
    elif args.y == 2014:
        tt_file = 'data/original/wc_2014_games_real.csv'
        mb_file = 'data/original/wc_2014_bets.csv'
        filter_start = "2014-06-12"
    else:
        tt_file = 'data/original/wc_2018_games_real.csv'
        mb_file = 'data/original/wc_2018_bets.csv'
        filter_start = "2018-06-13"

    prefix = f"{args.f}_{args.y}"

    dl = DataLoader(all_features, filter_start=filter_start)
    model_parameters = get_default_parameters()
    model_parameters["max_depth"] = 8
    model_parameters["max_features"] = "sqrt"
    model_parameters["min_samples_leaf"] = 1
    af_data = simulate(tt_file, mb_file, dl, model_parameters, f"{prefix}_all_features")

    dl = DataLoader(other_features, filter_start=filter_start)
    model_parameters["max_depth"] = 8
    model_parameters["max_features"] = "log2"
    model_parameters["min_samples_leaf"] = 10
    gf_data = simulate(tt_file, mb_file, dl, model_parameters, f"{prefix}_general_features")

    dl = DataLoader(player_features, filter_start=filter_start)
    model_parameters["max_depth"] = None
    model_parameters["max_features"] = "sqrt"
    model_parameters["min_samples_leaf"] = 5
    pf_data = simulate(tt_file, mb_file, dl, model_parameters, f"{prefix}_player_features")

    match_labels = [f"{get_country_code(game['home_team'])}-{get_country_code(game['away_team'])}" for _, game in af_data["simulation"].to_dict('index').items()]

    unit_strategies = [(af_data["unit"], "All features"), (gf_data["unit"], "General features"), (pf_data["unit"], "Player features")]
    plot_cum_returns(unit_strategies, f"{prefix}_unit", match_labels)

    kelly_strategies = [(af_data["kelly"], "All features"), (gf_data["kelly"], "General features"), (pf_data["kelly"], "Player features")]
    plot_cum_returns(kelly_strategies, f"{prefix}_kelly", match_labels)

    plot_bet_sizes(kelly_strategies, f"{prefix}_kelly_bet_fractions", match_labels)

    tournament_simulations = [(af_data["simulation"], "All features"), (gf_data["simulation"], "General features"), (pf_data["simulation"], "Player features")]
    plot_probabilities(tournament_simulations, f"{prefix}_probability", match_labels)
