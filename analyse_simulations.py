import glob
import pandas as pd

from simulation.analyse import get_win_probabilities

match_template = pd.read_csv('data/original/wc_2018_games.csv')
teams = pd.unique(match_template[['home_team', 'away_team']].values.ravel('K'))[0:32]
match_ids = match_template["id"]

simulations = pd.concat((pd.read_csv(f, index_col=None) for f in glob.glob("data/simulations/*.csv")))

results = get_win_probabilities(simulations, teams, match_ids)
