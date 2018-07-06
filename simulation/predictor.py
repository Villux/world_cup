import numpy as np

class Predictor():
    def __init__(self, outcome, home_score, away_score):
        self.outcome = outcome
        self.home_score = home_score
        self.away_score = away_score

    def get_score_from_goal_matrix(self, goal_matrix, outcome):
        if outcome == 1:
            a = np.tril(goal_matrix, -1)
            home_score, away_score = np.unravel_index(a.argmax(), a.shape)
            assert(home_score > away_score)
        elif outcome == 0:
            a = np.diag(goal_matrix)
            home_score, away_score = a.argmax() + 1, a.argmax() + 1
            assert(home_score == away_score)
        else:
            a = np.triu(goal_matrix, 1)
            home_score, away_score = np.unravel_index(a.argmax(), a.shape)
            assert(home_score < away_score)
        return home_score, away_score

    def predict_outcome_probabilities(self, x):
        return self.outcome.predict_proba(x)[0]

    def predict_score(self, x, outcome):
        home_score_proba = self.home_score.predict_proba(x)[0]
        away_score_proba = self.away_score.predict_proba(x)[0]

        N = len(home_score_proba)
        M = len(away_score_proba)
        min_shape = min(N, M)
        goal_matrix = np.outer(home_score_proba, away_score_proba)
        goal_matrix = goal_matrix[:min_shape, :min_shape]

        return self.get_score_from_goal_matrix(goal_matrix, outcome)

