import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import argparse
from multiprocessing import Pool, cpu_count

def get_team_data(row):
    columns = row.findChildren(['td'])

    team_name = columns[1].div.a.get_text()
    overall = int(columns[3].div.span.get_text())
    attack = int(columns[4].div.span.get_text())
    midfield = int(columns[5].div.span.get_text())
    defence = int(columns[6].div.span.get_text())

    return {
        'team': columns[1].div.a.get_text(),
        'overall': int(columns[3].div.span.get_text()),
        'attack': int(columns[4].div.span.get_text()),
        'midfield': int(columns[5].div.span.get_text()),
        'defence': int(columns[6].div.span.get_text())
    }

parser = argparse.ArgumentParser()
parser.add_argument('--year', type=str, default='17', help="Which year's FIFA")
args = parser.parse_args()

offset = 0
url = f'https://sofifa.com/teams/national?v={args.year}&offset=0'
page = requests.get(url)

print(f"Starting to scrape data for year {args.year}")

pool = Pool(cpu_count())

bs = BeautifulSoup(page.text, 'html.parser')
team_table  = bs.findAll('tbody')[0]

rows = team_table.findChildren(['tr'])
team_data = pool.map(get_team_data, rows)

team_df = pd.DataFrame(team_data)
team_df.to_csv(f"SOFIFA_national_{args.year}.csv")
