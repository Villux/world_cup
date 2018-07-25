import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from db.db_interface import get_connection

def append_player_data(df):
    query = ''' SELECT * from player_attribute;'''
    with get_connection() as conn:
        df_player_attribute = pd.read_sql(query, conn)
    df_player_attribute = df_player_attribute.drop(['id'], axis=1)

    dataset_w = df.shape[1]
    dataset = pd.merge(df, df_player_attribute,  how='left', left_on=['year','home_team'], right_on = ['year','nationality'])
    new_names = [(i, 'home_' + i) for i in dataset.iloc[:, dataset_w:].columns.values]
    dataset.rename(columns = dict(new_names), inplace=True)
    dataset = dataset.drop(['home_nationality'], axis=1)

    dataset_w = dataset.shape[1]
    dataset = pd.merge(dataset, df_player_attribute,  how='left', left_on=['year','away_team'], right_on = ['year','nationality'])
    new_names = [(i, 'away_' + i) for i in dataset.iloc[:, dataset_w:].columns.values]
    dataset.rename(columns = dict(new_names), inplace=True)
    dataset = dataset.drop(['away_nationality'], axis=1)
    return dataset

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
                ORDER BY date;'''
    with get_connection() as conn:
        return pd.read_sql(query, conn)

def merge_all_data():
    df_match = get_match_elo_and_goal()
    return append_player_data(df_match)

def switch_home_and_away(df):
    df = df.rename(columns={
        'home_team': 'away_team',
        'away_team': 'home_team',
        'home_score': 'away_score',
        'away_score': 'home_score',
        'home_elo': 'away_elo',
        'away_elo': 'home_elo',
        'home_goals_with_away': 'away_goals_with_home',
        'away_goals_with_home': 'home_goals_with_away',
        'home_goal_mean': 'away_goal_mean',
        'away_goal_mean': 'home_goal_mean',
        })
    df.loc[:, "goal_diff_with_away"] = df.loc[:, "goal_diff_with_away"].mul(-1)
    return df

def flip_wins(dataset, frac=0.20):
    return dataset.loc[(dataset["home_score"] > dataset["away_score"])].sample(frac=frac)

def get_dataset_with_balanced_wins(dataset):
    flip_df = flip_wins(dataset)
    flip_df = switch_home_and_away(flip_df)
    dataset.update(flip_df)
    return append_player_data(dataset)

def get_data(suffle=True, write_to_csv=False, save_filename="data/generated/master_data.csv"):
    match_data = get_match_elo_and_goal()
    if suffle:
        master_data = get_dataset_with_balanced_wins(match_data)
    else:
        master_data = merge_all_data()
    if write_to_csv:
        master_data.to_csv(save_filename, index=False)
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

def get_feature_columns():
    return ["elo_diff", "rating_diff", "potential_diff","height_diff", "weight_diff", "age_diff", "weak_foot_diff",
            "internationl_repuatiotion_diff", "crossing_diff", "finishing_diff", "heading_accuracy_diff",
            "short_passing_diff", "dribbling_diff", "fk_accuracy_diff", "long_passing_diff",
            'ball_control_diff', 'acceleration_diff', 'sprint_speed_diff', "reactions_diff",
            'shot_power_diff', 'stamina_diff', 'strength_diff', 'long_shots_diff',
            "aggression_diff", "penalties_diff", "marking_diff", "standing_tackle_diff",
            "away_goal_mean", "away_goals_with_home", "goal_diff_with_away", "home_goal_mean",
            "home_goals_with_away", "gk_diving_diff", "gk_handling_diff", "gk_kicking_diff", "gk_reflexes_diff"]

def get_feature_vector(dataset):
    dataset = calculate_relative_features(dataset)
    feature_columns = get_feature_columns()
    return dataset[feature_columns]

def get_dataset(flip=False):
    if flip:
        df_match = get_match_elo_and_goal()
        df_match = switch_home_and_away(df_match)
        dataset = append_player_data(df_match)
    else:
        dataset = get_data(suffle=True)
    dataset = dataset.dropna()
    return dataset

def get_train_test_wc_dataset(y_label, filter_start=None, filter_end=None):
    if y_label == "away_score":
        dataset = get_dataset(flip=True)
        y_label = "home_score"
    else:
        dataset = get_dataset()

    if y_label == "home_win":
        dataset.loc[:, y_label] = np.sign(dataset.home_score - dataset.away_score)

    if filter_start and filter_end:
        dataset = dataset.loc[(dataset['date'] < filter_start) | (dataset['date'] > filter_end)]
    elif filter_start:
        dataset = dataset.loc[dataset['date'] < filter_start]
    elif filter_end:
        dataset = dataset.loc[dataset['date'] > filter_end]

    no_friendly_or_wc = dataset[(dataset["tournament"] != "Friendly") & (dataset["tournament"] != "FIFA World Cup")]

    X = get_feature_vector(no_friendly_or_wc)
    y = no_friendly_or_wc[y_label]

    X_train, X_test, y_train, y_test = get_train_test_split(X, y)

    friendly_games = dataset[dataset["tournament"] == "Friendly"]
    X_friendly = get_feature_vector(friendly_games)
    y_friendly = friendly_games[y_label]

    X_train = pd.concat([X_train, X_friendly])
    y_train = pd.concat([y_train, y_friendly])

    wc_games = dataset[dataset["tournament"] == "FIFA World Cup"]
    X_wc = get_feature_vector(wc_games)
    y_wc = wc_games[y_label]

    X_test = pd.concat([X_test, X_wc])
    y_test = pd.concat([y_test, y_wc])
    return X_train, y_train, X_test, y_test, X_wc, y_wc

def get_whole_dataset(y_label, filter_start=None, filter_end=None):
    X_train, y_train, X_test, y_test, X_wc, y_wc = get_train_test_wc_dataset(y_label, filter_start=filter_start, filter_end=filter_end)

    X = pd.concat([X_train, X_test, X_wc])
    y = pd.concat([y_train, y_test, y_wc])
    return X, y

def get_train_test_split(X, y, size=0.25):
    return train_test_split(X, y, test_size=size, random_state=42)

if __name__ == "__main__":
    merge_all_data()
