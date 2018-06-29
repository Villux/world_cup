import requests
import json
import argparse
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument('--start', type=str, default='2018-6-01', help="Start date in form of YYYY-M-DD")
parser.add_argument('--end', type=str, default='2018-8-01', help="End date in form of YYYY-M-DD")
args = parser.parse_args()

url = f'https://data.fifa.com/livescores/en/internationaltournaments/matches/m/bydaterange/{args.start}/{args.end}'
page = requests.get(url)

page_txt = page.text[28:-1] # remove js function wrap
page_json = json.loads(page_txt)

game_data = page_json["competitionslist"]["0"]
matches = game_data["matchlist"]

all_matches = []
for match in matches:
    if match["isFinished"]:
        match_dict = {
            "date": match["matchDate"][:10],
            "home_team": match["homeTeamName"],
            "away_team": match["awayTeamName"],
            "home_score": int(match["scoreHome"]),
            "away_score": int(match["scoreAway"]),
            "year": int(match["matchDate"][:4]),
            "tournament": "FIFA World Cup",
            "city": match["venueName"],
            "country": "Russia",
            "neutral": False
        }
        all_matches.append(match_dict)

match_df = pd.DataFrame(all_matches)
match_df.to_csv(f"data/generated/fifa_match_results_{args.start}-{args.end}.csv")
