import numpy as np
from abc import ABCMeta, abstractmethod

def get_score_from_goal_matrix(goal_matrix, outcome):
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

class Predictor(metaclass=ABCMeta):
    @abstractmethod
    def predict_outcome_probabilities(self, x):
        pass

    @abstractmethod
    def predict_score(self, x):
        pass

class WDLPredictor(Predictor):
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
