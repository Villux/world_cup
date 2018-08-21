import os
import numpy as np
import pandas as pd
from dateutil.parser import parse
from sklearn.model_selection import train_test_split

from features.elo import get_elo
from features.generate_goal_features import calculate_goal_features_for_match
from db.db_interface import get_connection

other_features = ['elo_diff', 'away_goal_mean', 'away_goals_with_home',
                  'goal_diff_with_away', 'home_goal_mean', 'home_goals_with_away']

player_features = ['rating_diff', 'potential_diff', 'height_diff','weight_diff','age_diff',
                   'weak_foot_diff','internationl_repuatiotion_diff','crossing_diff','finishing_diff',
                   'heading_accuracy_diff','short_passing_diff','dribbling_diff','fk_accuracy_diff',
                   'long_passing_diff','ball_control_diff','acceleration_diff','sprint_speed_diff',
                   'reactions_diff','shot_power_diff','stamina_diff','strength_diff','long_shots_diff',
                   'aggression_diff','penalties_diff','marking_diff','standing_tackle_diff',
                  'gk_diving_diff', 'gk_handling_diff', 'gk_kicking_diff', 'gk_reflexes_diff']

all_features = other_features + player_features

def get_player_attribute_query(team, date):
    return f"SELECT * from player_attribute where nationality='{team}' AND date < '{date}' ORDER BY date desc LIMIT 1;"

def append_player_data(df):
    dataset = []
    for i in range(df.shape[0]):
        row = df.iloc[i].to_dict()

        for prefix in ["home", "away"]:
            team_key = f"{prefix}_team"
            query = get_player_attribute_query(row[team_key], row["date"])

            with get_connection() as conn:
                df_player_attribute = pd.read_sql(query, conn)
            df_player_attribute = df_player_attribute.drop(['id', 'date', 'nationality'], axis=1)
            if prefix == "home":
                new_names = [(i, "home_" + i) for i in df_player_attribute.columns.values]
            else:
                new_names = [(i, "away_" + i) for i in df_player_attribute.columns.values]
            df_player_attribute.rename(columns = dict(new_names), inplace=True)
            if df_player_attribute.shape[0] > 0:
                player_dict = df_player_attribute.iloc[0].to_dict()
                row = {**row, **player_dict}
        dataset.append(row)

    return pd.DataFrame(dataset)

def get_match_elo_and_goal():
    query = '''SELECT
                    m.*,
                    home_e.elo as "home_elo",
                    away_e.elo as "away_elo",
                    goal.goal_diff_with_away as "goal_diff_with_away",
                    goal.home_goals_with_away as "home_goals_with_away",
                    goal.away_goals_with_home as "away_goals_with_home",
                    goal.home_goal_mean as "home_goal_mean",
                    goal.away_goal_mean as "away_goal_mean"
                FROM match AS m
                LEFT JOIN elo_rating AS home_e
                    ON home_e.match_id=m.id AND home_e.team=m.home_team
                LEFT JOIN elo_rating AS away_e
                    ON away_e.match_id=m.id AND away_e.team=m.away_team
                LEFT JOIN goal_feature AS goal
                    ON goal.match_id=m.id
                WHERE m.date >= '2006-08-30'
                ORDER BY date;'''
    with get_connection() as conn:
        return pd.read_sql(query, conn)

def merge_all_data():
    df_match = get_match_elo_and_goal()
    return append_player_data(df_match)

def switch_home_and_away(df):
    renamed = {}
    for col in df.columns.values:
        if col[0:4] == "home":
            new_key = "away" + col[4:]
            renamed[col] = new_key
        elif col[0:4] == "away":
            new_key = "home" + col[4:]
            renamed[col] = new_key
    df = df.rename(columns=renamed)
    df = df.rename(columns={
        "home_goals_with_home": "home_goals_with_away",
        "away_goals_with_away": "away_goals_with_home"
    })
    df.loc[:, "goal_diff_with_away"] = df.loc[:, "goal_diff_with_away"].mul(-1)
    return df

def flip_wins(dataset, frac=0.20):
    return dataset.loc[(dataset["home_score"] > dataset["away_score"])].sample(frac=frac)

def get_dataset_with_balanced_wins(dataset):
    flip_df = flip_wins(dataset)
    flip_df = switch_home_and_away(flip_df)
    dataset.update(flip_df)
    return dataset

def get_original_data(cached_file="data/generated/master_data.csv"):
    if os.path.isfile(cached_file):
        master_data = pd.read_csv(cached_file)
    else:
        master_data = merge_all_data()
        master_data.to_csv(cached_file, index=False)
    return master_data

def calculate_relative_features(df):
    dataset = df.copy()
    dataset.loc[:, "elo_diff"] = dataset.home_elo - dataset.away_elo
    dataset.loc[:, "rating_diff"] = dataset.home_overall_rating_avg - dataset.away_overall_rating_avg
    dataset.loc[:, "potential_diff"] = dataset.home_potential_avg - dataset.away_potential_avg
    dataset.loc[:, "height_diff"] = dataset.home_height - dataset.away_height
    dataset.loc[:, "weight_diff"] = dataset.home_weight - dataset.away_weight
    dataset.loc[:, "age_diff"] = dataset.home_age - dataset.away_age
    dataset.loc[:, "weak_foot_diff"] = dataset.home_weak_foot - dataset.away_weak_foot
    dataset.loc[:, "internationl_repuatiotion_diff"] = dataset.home_international_reputation - dataset.away_international_reputation
    dataset.loc[:, "crossing_diff"] = dataset.home_Crossing - dataset.away_Crossing
    dataset.loc[:, "finishing_diff"] = dataset.home_Finishing - dataset.away_Finishing
    dataset.loc[:, "heading_accuracy_diff"] = dataset.home_Heading_Accuracy - dataset.away_Heading_Accuracy
    dataset.loc[:, "short_passing_diff"] = dataset.home_Short_Passing - dataset.away_Short_Passing
    dataset.loc[:, "dribbling_diff"] = dataset.home_Dribbling - dataset.away_Dribbling
    dataset.loc[:, "fk_accuracy_diff"] = dataset.home_FK_Accuracy - dataset.away_FK_Accuracy
    dataset.loc[:, "long_passing_diff"] = dataset.home_Long_Passing - dataset.away_Long_Passing
    dataset.loc[:, "ball_control_diff"] = dataset.home_Ball_Control - dataset.away_Ball_Control
    dataset.loc[:, "acceleration_diff"] = dataset.home_Acceleration - dataset.away_Acceleration
    dataset.loc[:, "sprint_speed_diff"] = dataset.home_Sprint_Speed - dataset.away_Sprint_Speed
    dataset.loc[:, "reactions_diff"] = dataset.home_Reactions - dataset.away_Reactions
    dataset.loc[:, "shot_power_diff"] = dataset.home_Shot_Power - dataset.away_Shot_Power
    dataset.loc[:, "stamina_diff"] = dataset.home_Stamina - dataset.away_Stamina
    dataset.loc[:, "strength_diff"] = dataset.home_Strength - dataset.away_Strength
    dataset.loc[:, "long_shots_diff"] = dataset.home_Long_Shots - dataset.away_Long_Shots
    dataset.loc[:, "aggression_diff"] = dataset.home_Aggression - dataset.away_Aggression
    dataset.loc[:, "penalties_diff"] = dataset.home_Penalties - dataset.away_Penalties
    dataset.loc[:, "marking_diff"] = dataset.home_Marking - dataset.away_Marking
    dataset.loc[:, "standing_tackle_diff"] = dataset.home_Standing_Tackle - dataset.away_Standing_Tackle
    dataset.loc[:, "gk_diving_diff"] = dataset.home_GK_Diving - dataset.away_GK_Diving
    dataset.loc[:, "gk_handling_diff"] = dataset.home_GK_Handling - dataset.away_GK_Handling
    dataset.loc[:, "gk_kicking_diff"] = dataset.home_GK_Kicking - dataset.away_GK_Kicking
    dataset.loc[:, "gk_reflexes_diff"] = dataset.home_GK_Reflexes - dataset.away_GK_Reflexes
    return dataset

def get_feature_vector(dataset, feature_columns):
    dataset = calculate_relative_features(dataset)
    return dataset[feature_columns]

def get_dataset(flip=False, suffle=False):
    dataset = get_original_data()
    dataset = dataset.dropna()

    if suffle:
        dataset = get_dataset_with_balanced_wins(dataset)
    if flip:
        dataset = switch_home_and_away(dataset)
    return dataset

def get_train_test_split(X, y, size=0.25, random_state=42):
    return train_test_split(X, y, test_size=size, random_state=42) if random_state else train_test_split(X, y, test_size=size)

def load_all_data_by_label(y_label):
    if y_label == "away_score":
        dataset = get_dataset(flip=True, suffle=False)
        y_label = "home_score"
    else:
        dataset = get_dataset(flip=False)
    if y_label == "home_win":
        dataset = get_dataset(suffle=True)
        dataset.loc[:, y_label] = np.sign(dataset.home_score - dataset.away_score)

    return dataset, y_label

class DataLoader():
    def __init__(self, features, filter_start=None, filter_end=None, interval=None):
        self.feature_columns = features
        self.filter_start = filter_start
        self.filter_end = filter_end
        self.interval = interval

    def filter_data(self, dataset):
        if self.filter_start and self.filter_end:
            dataset = dataset.loc[(dataset['date'] < self.filter_start) | (dataset['date'] > self.filter_end)]
        elif self.filter_start:
            dataset = dataset.loc[dataset['date'] < self.filter_start]
        elif self.filter_end:
            dataset = dataset.loc[dataset['date'] > self.filter_end]

        if self.interval:
            dataset = dataset.loc[(dataset['date'] > self.interval[0]) & (dataset['date'] < self.interval[1])]

        return dataset

    def get_train_and_test_dataset(self, y_label, random_state=42):
        dataset, y_label = load_all_data_by_label(y_label)
        dataset = self.filter_data(dataset)

        no_friendly_or_wc = dataset[(dataset["tournament"] != "Friendly") & (dataset["tournament"] != "FIFA World Cup")]

        X = get_feature_vector(no_friendly_or_wc, self.feature_columns)
        y = no_friendly_or_wc[y_label]

        X_train, X_test, y_train, y_test = get_train_test_split(X, y, random_state=random_state)

        wc_games = dataset[dataset["tournament"] == "FIFA World Cup"]
        X_wc = get_feature_vector(wc_games, self.feature_columns)
        y_wc = wc_games[y_label]

        X_test = pd.concat([X_test, X_wc])
        y_test = pd.concat([y_test, y_wc])
        return X_train, y_train, X_test, y_test

    def get_merged_dataset(self, y_label):
        X_train, y_train, X_test, y_test = self.get_train_and_test_dataset(y_label)

        X = pd.concat([X_train, X_test])
        y = pd.concat([y_train, y_test])

        return X, y

    def get_all_data(self, y_label):
        if isinstance(y_label, list):
            A, b = self.get_merged_dataset(y_label[0])
            C, d = self.get_merged_dataset(y_label[1])
            return A, b, C, d
        return self.get_merged_dataset(y_label)

    def get_match_feature_vector(self, match):
        data_merge_obj = {"home_team": match.home_team, "away_team": match.away_team, "date": match.date}
        data_merge_obj["year"] = parse(match.date).year

        # ELO
        home_elo = get_elo(match.home_team, match.date)
        away_elo = get_elo(match.away_team, match.date)
        data_merge_obj["home_elo"] = home_elo
        data_merge_obj["away_elo"] = away_elo

        # Goals
        goal_data = calculate_goal_features_for_match(match.date, match.home_team, match.away_team)
        for key, value in goal_data.items():
            data_merge_obj[key] = value

        # Player data
        data_merge_obj = pd.DataFrame([data_merge_obj])
        data_merge_obj = append_player_data(data_merge_obj)
        return get_feature_vector(data_merge_obj, self.feature_columns)

    def set_filter_start(self, start):
        self.filter_start = start
