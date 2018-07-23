import pandas as pd

def get_win_probabilities(simulatios, teams, match_ids):
    results = []

    for match_id in match_ids:
        matches = simulatios.loc[simulatios['match_id'] == match_id]
        total = matches.shape[0]

        for team in teams:
            matches_for_team = matches.loc[(matches['home_team'] == team) | (matches["away_team"] == team), "outcome"].count()
            if matches_for_team == 0:
                continue
            home_wins = matches.loc[(matches['home_team'] == team) & (matches["outcome"] == 1), "outcome"].count()
            away_wins = matches.loc[(matches['away_team'] == team) & (matches["outcome"] == -1), "outcome"].count()

            win_prob = (home_wins + away_wins) / matches_for_team

            home_draw = matches.loc[(matches['home_team'] == team) & (matches["outcome"] == 0), "outcome"].count()
            away_draw = matches.loc[(matches['away_team'] == team) & (matches["outcome"] == 0), "outcome"].count()
            draw_prob = (home_draw + away_draw) / matches_for_team

            lose_prob = 1 - win_prob - draw_prob

            prob_dict = {
                "match_id": match_id,
                "team": team,
                "plays_match_prob": matches_for_team/total,
                "win_prob": win_prob,
                "draw_prob": draw_prob,
                "lose_prob": lose_prob,
            }
            results.append(prob_dict)

    return pd.DataFrame(results)
