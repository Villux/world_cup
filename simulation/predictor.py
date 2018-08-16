import numpy as np
from scipy.stats import poisson

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

class OutcomePredictor():
    def __init__(self, model, data_loader):
        self.model = model
        self.data_loader = data_loader

    @staticmethod
    def predict_score(outcome):
        home_goals, away_goals = 0, 0
        if outcome == 1:
            home_goals = 1
        elif outcome == -1:
            away_goals = 1
        return home_goals, away_goals

    @staticmethod
    def sample_outcome(outcome_probabilities):
        return int(np.random.choice([-1, 0, 1], 1, p=outcome_probabilities)[0])

    def predict_outcome_probabilities(self, x):
        return self.model.predict_proba(x)[0]

    def predict(self, match):
        x = self.data_loader.get_match_feature_vector(match)
        match.set_feature_vector(x)

        outcome_probabilities = self.predict_outcome_probabilities(x)
        match.set_outcome_probabilties(outcome_probabilities)

        outcome = self.sample_outcome(outcome_probabilities)
        match.set_outcome(outcome)
        home_score, away_score = self.predict_score(outcome)
        match.set_score(home_score, away_score)
        return match

class MaxProbabilityOutcomePredictor(OutcomePredictor):
    def __init__(self, model, data_loader):
        super().__init__(model, data_loader)
        self.model = model
        self.data_loader = data_loader

    def predict(self, match):
        x = self.data_loader.get_match_feature_vector(match)
        match.set_feature_vector(x)

        outcome_probabilities = self.predict_outcome_probabilities(x)
        match.set_outcome_probabilties(outcome_probabilities)

        outcome = np.argmax(outcome_probabilities) - 1
        match.set_outcome(outcome)
        home_score, away_score = self.predict_score(outcome)
        match.set_score(home_score, away_score)
        return match

class ScorePredictor():
    def __init__(self, model, data_loader):
        self.model = model
        self.data_loader = data_loader

    @staticmethod
    def get_goal_matrix(home_mu, away_mu):
        home_goal_prob, away_goal_prob = [[poisson.pmf(i, team_avg) for i in range(0, 11)] for team_avg in [home_mu, away_mu]]
        return np.outer(home_goal_prob, away_goal_prob)

    @staticmethod
    def get_outcome_probabilities(goal_matrix):
        home_win = np.sum(np.tril(goal_matrix, -1))
        draw = np.sum(np.diag(goal_matrix))
        away_win = np.sum(np.triu(goal_matrix, 1))

        return [away_win, draw, home_win]

    def predict_score(self, x):
        mu_score = self.model.predict(x)[0]
        p = poisson(mu_score)
        return p.rvs(), mu_score

    def predict(self, match):
        away_match = match.flip_and_copy()

        home_x = self.data_loader.get_match_feature_vector(match)
        home_score, home_mu = self.predict_score(home_x)

        away_x = self.data_loader.get_match_feature_vector(away_match)
        away_score, away_mu = self.predict_score(away_x)

        goal_matrix = self.get_goal_matrix(home_mu, away_mu)
        outcome_probabilities = self.get_outcome_probabilities(goal_matrix)
        match.set_outcome_probabilties(outcome_probabilities)

        match.set_score(home_score, away_score)
        match.set_outcome_from_score()
        return match

class MaxProbabilityScorePredictor(ScorePredictor):
    def __init__(self, model, data_loader):
        super().__init__(model, data_loader)
        self.model = model
        self.data_loader = data_loader

    def predict(self, match):
        away_match = match.flip_and_copy()

        home_x = self.data_loader.get_match_feature_vector(match)
        _, home_mu = self.predict_score(home_x)

        away_x = self.data_loader.get_match_feature_vector(away_match)
        _, away_mu = self.predict_score(away_x)

        goal_matrix = self.get_goal_matrix(home_mu, away_mu)
        outcome_probabilities = self.get_outcome_probabilities(goal_matrix)
        match.set_outcome_probabilties(outcome_probabilities)

        outcome = np.argmax(outcome_probabilities) - 1
        home_score, away_score = get_score_from_goal_matrix(goal_matrix, outcome)
        match.set_outcome(outcome)
        match.set_score(home_score, away_score)
        return match

class OneVsRestPredictor():
    def __init__(self, home_model, draw_model, away_model, data_loader):
        self.home_model = home_model
        self.draw_model = draw_model
        self.away_model = away_model
        self.data_loader = data_loader

    @staticmethod
    def predict_score(outcome):
        home_goals, away_goals = 0, 0
        if outcome == 1:
            home_goals = 1
        elif outcome == -1:
            away_goals = 1
        return home_goals, away_goals


    def predict_outcome_probabilities(self, x):
        home_win_prob = self.home_model.predict_proba(x)[0][1]
        draw_prob = self.draw_model.predict_proba(x)[0][1]
        away_win_prob = self.away_model.predict_proba(x)[0][1]

        probas = np.array([away_win_prob, draw_prob, home_win_prob])
        probas = probas / probas.sum()
        return probas

    def predict(self, match):
        x = self.data_loader.get_match_feature_vector(match)
        match.set_feature_vector(x)

        outcome_probabilities = self.predict_outcome_probabilities(x)
        match.set_outcome_probabilties(outcome_probabilities)
        outcome = np.argmax(outcome_probabilities) - 1
        match.set_outcome(outcome)
        home_score, away_score = self.predict_score(outcome)
        match.set_score(home_score, away_score)
        return match
