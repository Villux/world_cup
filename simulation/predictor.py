import numpy as np
import pandas as pd
from dateutil.parser import parse
from scipy.stats import poisson

from features.elo import get_current_elo, attach_elo_to_match
from features.generate_goal_features import calculate_goal_features_for_match
from features.data_provider import append_player_data, get_feature_vector

def get_score_from_goal_matrix(goal_matrix, outcome):
    if outcome == 1:
        a = np.tril(goal_matrix, -1)
        home_score, away_score = np.unravel_index(a.argmax(), a.shape)
        assert home_score > away_score
    elif outcome == 0:
        a = np.diag(goal_matrix)
        home_score, away_score = a.argmax() + 1, a.argmax() + 1
        assert home_score == away_score
    else:
        a = np.triu(goal_matrix, 1)
        home_score, away_score = np.unravel_index(a.argmax(), a.shape)
        assert home_score < away_score
    return home_score, away_score

def get_outcome_probabilities(goal_matrix):
    home_win = np.sum(np.tril(goal_matrix, -1))
    draw = np.sum(np.diag(goal_matrix))
    away_win = np.sum(np.triu(goal_matrix, 1))

    return [away_win, draw, home_win]

def get_match_feature_vector(match):
    data_merge_obj = {"home_team": match.home_team, "away_team": match.away_team, "date": match.date}
    data_merge_obj["year"] = parse(match.date).year

    # ELO
    home_elo = get_current_elo(match.home_team)
    away_elo = get_current_elo(match.away_team)
    data_merge_obj["home_elo"] = home_elo
    data_merge_obj["away_elo"] = away_elo

    # Goals
    goal_data = calculate_goal_features_for_match(match.date, match.home_team, match.away_team)
    for key, value in goal_data.items():
        data_merge_obj[key] = value

    # Player data
    data_merge_obj = pd.DataFrame([data_merge_obj])
    data_merge_obj = append_player_data(data_merge_obj)
    return get_feature_vector(data_merge_obj)

class WDLPredictor():
    def __init__(self, model):
        self.model = model

    def predict_outcome_probabilities(self, x):
        return self.model.predict_proba(x)[0]

    def predict_score(self, x):
        home_goals, away_goals = 0, 0
        outcome = self.model.predict(x)
        if outcome == 1:
            home_goals = 1
        elif outcome == -1:
            away_goals = 1
        return home_goals, away_goals

    def predict(self, match):
        x = get_match_feature_vector(match)
        match.set_feature_vector(x)

        outcome_probabilities = self.predict_outcome_probabilities(x)
        match.set_outcome_probabilties(outcome_probabilities)

        home_score, away_score = self.predict_score(x)
        match.set_score(home_score, away_score)
        return match

class ScorePredictor():
    def __init__(self, model):
        self.model = model

    def predict_score(self, x):
        mu_score = self.model.predict(x)[0]
        p = poisson(mu_score)
        return p.rvs(), mu_score

    def predict_outcome_probabilities(self, home_mu, away_mu):
        home_goal_prob, away_goal_prob = [[poisson.pmf(i, team_avg) for i in range(0, 11)] for team_avg in [home_mu, away_mu]]
        goal_matrix = np.outer(home_goal_prob, away_goal_prob)
        return get_outcome_probabilities(goal_matrix)

    def predict(self, match):
        away_match = match.flip_and_copy()

        home_x = get_match_feature_vector(match)
        home_score, home_mu = self.predict_score(home_x)

        away_x = get_match_feature_vector(away_match)
        away_score, away_mu = self.predict_score(away_x)

        outcome_probabilities = self.predict_outcome_probabilities(home_mu, away_mu)
        match.set_outcome_probabilties(outcome_probabilities)

        match.set_score(home_score, away_score)
        match.set_outcome_from_score()
        return match
