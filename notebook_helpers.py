import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from simulation.analyse import get_win_probabilities, get_simulations

def plot_bank_and_bets(banks, bets, results):
    colors = {0: 'r', 1: 'g'}
    fig, ax = plt.subplots(figsize=(12, 12))
    index = np.arange(len(bets))
    ax.bar(index, bets, color=[colors[i] for i in results]) 
    ax.plot(banks)
    ax.set_xticks(np.arange(0, 64))
    plt.xticks(rotation='vertical')
    
def run_unit_strategy(y_pred, y_true, odds, initial_capital=64, bet_size=1, plot=False):
    bets = []
    banks = []
    results = []

    bank = initial_capital

    for i in range(len(y_true)):
        if bank <= bet_size:
            print("Bank empty")
            break

        banks.append(bank)
        bets.append(bet_size)

        bank -= bet_size
        predicted_outcome = y_pred[i]
        if y_true[i] == predicted_outcome:
            if predicted_outcome == 1:
                odd = odds[i, 0]
            elif predicted_outcome == 0:
                odd = odds[i, 1]
            else:
                odd = odds[i, 2]
            bank += odd * bet_size
            results.append(1)
        else:
            results.append(0)
                
    if plot:
        print(f"Profit: {np.around((bank/initial_capital - 1)*100, 4)}%")
        print("Balance: ", bank)
        plot_bank_and_bets(banks, bets, results)
    return bank
    
def run_kelly_strategy(y_pred, y_true, odds, probabilities, initial_capital=64, plot=False):
    bank = initial_capital

    bets = []
    banks = []
    results = []
    for i in range(len(y_true)):
        predicted_outcome = y_pred[i]
        if predicted_outcome == 1:
            odd = odds[i, 0]
            p = probabilities[i, 0]
        elif predicted_outcome == 0:
            odd = odds[i, 1]
            p = probabilities[i, 1]
        else:
            odd = odds[i, 2]
            p = probabilities[i, 2]

        b = odd-1
        q = 1-p
        f = max((b*p - q)/b, 0)
        bet_size = bank * f

        bets.append(bet_size)

        bank -= bet_size

        if y_true[i] == predicted_outcome:
            win = odd * bet_size
            bank += win
            results.append(1)
        else:
            results.append(0)
        banks.append(bank)

    if plot:
        print(f"Profit: {np.around((bank/initial_capital - 1)*100, 4)}%")
        print("Balance: ", bank)
        plot_bank_and_bets(banks, bets, results)
    return bank
    
def get_tournament_results(simulations_files, tournament_template_file, filename=None):
    tournament_template = pd.read_csv(tournament_template_file)
    teams = pd.unique(tournament_template[['home_team', 'away_team']].values.ravel('K'))[0:32]
    match_ids = tournament_template["id"]

    simulations = get_simulations(simulations_files)
    simulations.shape

    match_wise_probabilities = get_win_probabilities(simulations, teams, match_ids)

    match_simulations = []

    tournament_template.set_index('id')
    for i in range(tournament_template.shape[0]):
        match_id = tournament_template.loc[i, "id"]
        away_team = tournament_template.loc[i, "away_team"]
        home_team = tournament_template.loc[i, "home_team"]

        home_win_prob = match_wise_probabilities.loc[
            (match_wise_probabilities["match_id"] == match_id) & 
            (match_wise_probabilities["team"] == home_team), "win_prob"].item()

        away_win_prob = match_wise_probabilities.loc[
            (match_wise_probabilities["match_id"] == match_id) & 
            (match_wise_probabilities["team"] == away_team), "win_prob"].item()

        draw_prob = 1 - home_win_prob - away_win_prob

        if (home_win_prob > away_win_prob) and (home_win_prob > draw_prob):
            outcome = 1
        elif (away_win_prob > home_win_prob) and (away_win_prob > draw_prob):
            outcome = -1
        else:
            outcome = 0

        match_simulation = {
            "home_team": home_team,
            "away_team": away_team,
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob, 
            "away_win_prob": away_win_prob,
            "outcome": outcome,
            "true_outcome": np.sign(tournament_template.loc[i, "home_score"] - tournament_template.loc[i, "away_score"])
        }
        match_simulations.append(match_simulation)

    tournament_simulation = pd.DataFrame(match_simulations)
    if filename:
        tournament_simulation.to_csv(filename)

    print("Accuracy:", sum(tournament_simulation["outcome"] == tournament_simulation["true_outcome"]) / tournament_template.shape[0])
    return tournament_simulation