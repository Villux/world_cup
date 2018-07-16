import numpy as np

class Match():
    def __init__(self, data, win_or_lose=False):
        self.id = data["id"]
        self.home_team = data.get("home_team", None)
        self.away_team = data.get("away_team", None)
        self.home_score = data.get("home_score", None)
        self.away_score = data.get("away_score", None)
        self.tournament = data.get("tournament", "FIFA World Cup")
        self.group = data.get("group", None)
        self.date = data.get("date", None)
        self.outcome_probabilities = None
        self.outcome = None
        self.win_or_lose = win_or_lose

        self.feature_vector = None

    def set_feature_vector(self, x):
        self.feature_vector = x

    def set_outcome_probabilties(self, outcome_probabilities):
        assert len(outcome_probabilities) > 2
        if self.win_or_lose:
            self.outcome_probabilities = [outcome_probabilities[0], None, outcome_probabilities[2]]
        else:
            self.outcome_probabilities = outcome_probabilities

    def set_score(self, home_score, away_score):
        self.home_score = home_score
        self.away_score = away_score

    def get_outcome_probabilties(self):
        return self.outcome_probabilities

    def get_outcome_from_probabilites(self):
        return np.argmax(self.outcome_probabilities) - 1

    def get_outcome(self):
        if self.outcome is None:
            return self.get_outcome_from_probabilites()
        else:
            return self.outcome

    def to_dict(self):
        return {
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "tournament": self.tournament,
            "date": self.date
        }