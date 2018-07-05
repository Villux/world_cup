import functools
import random
import numpy as np
import pandas as pd
from dateutil.parser import parse

from generate_goal_features import calculate_goal_features_for_match
from data_provider import append_player_data, get_feature_vector
from match_table import insert
from elo import update_elo_after_match, get_current_elo, attach_elo_to_match
from match_table import delete_simulations
from elo_table import delete_elos_after_date

def get_match_feature_vector(df):
    home_team = df["home_team"]
    away_team = df["away_team"]
    date = df["date"]
    df["year"] = parse(date).year

    # ELO
    home_elo = get_current_elo(home_team)
    away_elo = get_current_elo(away_team)
    df["home_elo"] = home_elo
    df["away_elo"] = away_elo

    # Goals
    goal_data = calculate_goal_features_for_match(date, home_team, away_team)
    for key, value in goal_data.items():
        df[key] = value

    # Player data
    df = pd.DataFrame([df])
    df = append_player_data(df)
    return df

def post_match_results(df):
    df = df.iloc[0].to_dict()
    home_team = df["home_team"]
    away_team = df["away_team"]
    date = df["date"]
    home_score = df["home_score"]
    away_score = df["away_score"]
    tournament = df["tournament"]

    match = {
        "date": date,
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
        "tournament": tournament,
        "year": df["year"],
        "simulation": True
    }

    match_id = insert(**match)

    home_elo, away_elo = attach_elo_to_match(match_id, home_team, away_team)
    update_elo_after_match(date, home_elo, away_elo, home_team, away_team, home_score, away_score, tournament)

def post_simulation():
    simulation_start_date = "2018-06-13"
    delete_elos_after_date(simulation_start_date)
    delete_simulations()

class GroupTable():
    def __init__(self, matches):
        self.matches = matches
        self.table = self.build_group_table()

    def build_group_table(self):
        data = []
        for key, value in self.matches.groupby('group')['home_team'].unique().to_dict().items():
            for team in value:
                data.append({"Team": team, "Group": key, "points": 0, 'goal_diff': 0, 'goals_scored': 0})

        return pd.DataFrame(data)

    def print_group_standings(self):
        self.sort()
        columns = ['Position', 'Group A', 'Points A', 'Group B', 'Points B', 'Group C', 'Points C',
                'Group D', 'Points D', 'Group E', 'Points E', 'Group F', 'Points F',
                'Group G', 'Points G', 'Group H', 'Points H']

        data = {"Position": [1,2,3,4]}
        df = pd.DataFrame(data, columns = columns)

        for idx, group in enumerate(["A", "B", "C", "D", "E", "F", "G", "H"]):
            group_df = self.table[self.table["Group"] == group]
            group_df = group_df.reset_index()
            group_df = group_df.drop(['index', 'Group'], axis=1)
            df.iloc[:, 1 + (idx * 2)] = group_df["Team"]
            df.iloc[:, 2 + (idx * 2)] = group_df["points"]

        print("\n\n", df)

    def sort(self):
        sorted_table = pd.DataFrame()
        for group in np.unique(self.table["Group"]):
            group_df = self.table[self.table["Group"] == group]
            teams = [group_df.iloc[0], group_df.iloc[1], group_df.iloc[2], group_df.iloc[3]]
            shorted_standing = sorted(teams, key=functools.cmp_to_key(self.get_better_team))
            tmp = pd.concat([row.to_frame().T for row in shorted_standing])
            sorted_table = pd.concat([sorted_table, tmp])
        self.table = sorted_table

    def update_table(self, match, match_sign):
        if match_sign == 1:
            self.table.loc[self.table["Team"] == match["home_team"], "points"] += 3
        elif match_sign == 0:
            self.table.loc[self.table["Team"] == match["home_team"], "points"] += 1
            self.table.loc[self.table["Team"] == match["away_team"], "points"] += 1
        elif match_sign == -1:
            self.table.loc[self.table["Team"] == match["away_team"], "points"] += 3
        self.sort()

    def get_team(self, group, position):
        return self.table[self.table["Group"] == group].iloc[position]["Team"]

    def store_mutual_match(self, match):
        home = match["home_team"]
        away = match["away_team"]
        self.table[f"{home}-{away}"] = match["home_score"] - match["away_score"]
        self.table[f"{away}-{home}"] = match["away_score"] - match["home_score"]

    def get_better_team(self, first_team, second_team):
        if first_team["points"] > second_team["points"]:
            return -1
        elif first_team["points"] < second_team["points"]:
            return 1

        if first_team["goal_diff"] > second_team["goal_diff"]:
            return -1
        elif first_team["goal_diff"] < second_team["goal_diff"]:
            return 1

        if first_team["goals_scored"] > second_team["goals_scored"]:
            return -1
        elif first_team["goals_scored"] < second_team["goals_scored"]:
            return 1

        f_name = first_team["Team"]
        s_name = second_team["Team"]
        if first_team[f"{f_name}-{s_name}"] > 0:
            return -1
        elif first_team[f"{f_name}-{s_name}"] < 0:
            return 1
        else:
            return - 1 if random.random() > 0.5 else -1

class WorldCup():
    def __init__(self, matches, table, sign_model, verbose=True):
        self.matches = matches
        self.group_table = table
        self.sign_model = sign_model
        self.verbose = verbose

    def print(self, text, end='\n'):
        if self.verbose:
            print(text, end=end)

    def get_sign_from_probabilities(self, sign_probabilities, win_or_loose=False):
        probas = sign_probabilities
        if win_or_loose:
            probas[1] = 0.0
        sign = np.argmax(probas)
        return sign - 1

    def predict_match_outcome(self, match):
        data = get_match_feature_vector(match)
        x = get_feature_vector(data)

        probas = self.sign_model.predict_proba(x)

        data["home_score"] = 0
        data["away_score"] = 0
        data["tournament"] = "FIFA World Cup"
        data["year"] = 2018
        post_match_results(data)

        return probas[0]

    def print_match_result(self, match_sign, probas, match):
        if "home_win" in match and match_sign != match.get("home_win", 100):
            self.print(f"\x1b[31m{match['home_team']} - {match['away_team']}: \x1b[0m", end='')
        else:
            self.print(f"{match['home_team']} - {match['away_team']}: ", end='')
        self.print(f"{match_sign} -- PROBAS -- {probas}")

    def simulate_group_stage(self):
        self.print("\n\n\n___Group Stage___\n")

        for _, match in self.matches.iloc[0:48].iterrows():
            match = match.to_dict()
            match["home_win"] = np.sign(match["home_score"] - match["away_score"])

            probas = self.predict_match_outcome(match)
            match_sign = self.get_sign_from_probabilities(probas)
            self.print_match_result(match_sign, probas, match)

            self.group_table.update_table(match, match_sign)

            self.group_table.store_mutual_match(match)

    def simulate_round_of_16(self):
        i = 0
        self.print("\n\n\n___Round of 16___\n")
        for index, match in self.matches.iloc[48:56].iterrows():
            home_group, home_position = list(match["home_team"])
            away_group, away_position = list(match["away_team"])

            self.matches.loc[index, "home_team"] = self.group_table.get_team(home_group, int(home_position) - 1)
            self.matches.loc[index, "away_team"] = self.group_table.get_team(away_group, int(away_position) - 1)

            match = self.matches.loc[index].to_dict()
            probas = self.predict_match_outcome(match)
            match_sign = self.get_sign_from_probabilities(probas, win_or_loose=True)

            self.print_match_result(match_sign, probas, match)

            team_col = "home_team" if index%2 == 0 else "away_team"
            if match_sign == 1:
                self.matches.loc[56 + i, team_col] = match["home_team"]
            else:
                self.matches.loc[56 + i, team_col] = match["away_team"]
            if index%2 != 0:
                i += 1

    def simulate_quarter_finals(self):
        i = 0
        self.print("\n\n\n___Quarter-Finals___\n")
        for index, match in self.matches.iloc[56:60].iterrows():
            match = self.matches.loc[index].to_dict()
            probas = self.predict_match_outcome(match)
            match_sign = self.get_sign_from_probabilities(probas, win_or_loose=True)
            self.print_match_result(match_sign, probas, match)

            team_col = "home_team" if index%2 == 0 else "away_team"
            if match_sign == 1:
                self.matches.loc[60 + i, team_col] = match["home_team"]
            else:
                self.matches.loc[60 + i, team_col] = match["away_team"]
            if index%2 != 0:
                i += 1

    def simulate_semi_finals(self):
        self.print("\n\n\n___Semi-Finals___\n")
        for index, match in self.matches.iloc[60:62].iterrows():
            match = self.matches.loc[index].to_dict()
            probas = self.predict_match_outcome(match)
            match_sign = self.get_sign_from_probabilities(probas, win_or_loose=True)
            self.print_match_result(match_sign, probas, match)

            team_col = "home_team" if index%2 == 0 else "away_team"
            if match_sign == 1:
                self.matches.loc[63, team_col] = match["home_team"]
                self.matches.loc[62, team_col] = match["away_team"]
            else:
                self.matches.loc[63, team_col] = match["away_team"]
                self.matches.loc[62, team_col] = match["home_team"]

    def simulate_third_place_play_off(self):
        self.print("\n\n\n___Third place play-off___\n")
        for index, match in self.matches.iloc[62:63].iterrows():
            match = self.matches.loc[index].to_dict()
            probas = self.predict_match_outcome(match)
            match_sign = self.get_sign_from_probabilities(probas, win_or_loose=True)
            self.print_match_result(match_sign, probas, match)

    def simulate_finals(self):
        self.print("\n\n\n___Final___\n")
        for index, match in self.matches.iloc[63:].iterrows():
            match = self.matches.loc[index].to_dict()
            probas = self.predict_match_outcome(match)
            match_sign = self.get_sign_from_probabilities(probas, win_or_loose=True)
            self.print_match_result(match_sign, probas, match)

    def simulate_tournament(self):
        self.simulate_group_stage()
        self.group_table.print_group_standings()
        self.simulate_round_of_16()
        self.simulate_quarter_finals()
        self.simulate_semi_finals()
        self.simulate_third_place_play_off()
        self.simulate_finals()

def run_simulation(sign_model):
    wc_2018_matches = pd.read_csv('data/original/wc_2018_games.csv')
    group_table = GroupTable(wc_2018_matches)
    wc_2018 = WorldCup(wc_2018_matches, group_table, sign_model)

    wc_2018.simulate_tournament()
    post_simulation()
