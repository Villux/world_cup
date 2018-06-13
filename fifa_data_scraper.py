import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import argparse

def get_nationality(playerPage):
    link = playerPage.a["href"]
    page = requests.get('http://www.futhead.com/' + link)
    bs = BeautifulSoup(page.text, 'html.parser')
    nationality = bs.findAll('div', {'class': 'player-sidebar-item'})[2].a.get_text()
    if len(nationality) == 0:
        nationality = ' '
    return nationality


nationality_cache = {}
def get_nationality_from_cache(cache_key):
    if cache_key in nationality_cache:
        return nationality_cache[cache_key]
    else:
        return None


parser = argparse.ArgumentParser()
parser.add_argument('--year', type=int, default=17, help="Which year's FIFA")
args = parser.parse_args()

key = args.year


# Runtime start
start = time.clock()
print(start)

# Sending request to futhead.com
FutHead = requests.get('http://www.futhead.com/18/players')

# Parsing the number of pages for fifa 18 players
bs = BeautifulSoup(FutHead.text, 'html.parser')
TotalPages = int(re.sub('\s +', '', str(bs.find('span', {'class': 'font-12 font-bold margin-l-r-10'}).get_text())).split(' ')[1])
print('Number of pages to be parsed: ' + str(TotalPages))

fifa = {
    '10': 'FIFA10',
    '11': 'FIFA11',
    '12': 'FIFA12',
    '13': 'FIFA13',
    '14': 'FIFA14',
    '15': 'FIFA15',
    '16': 'FIFA16',
    '17': 'FIFA17',
    '18': 'FIFA18'
}

print(f'Doing Fifa {key}')

# List Intializations
players = []

# Looping through all pages to retrieve players stats and information
for page in range(1, TotalPages + 1):
    FutHead = requests.get('http://www.futhead.com/' + str(key) + '/players/?page=' + str(page) + '&bin_platform=ps')
    bs = BeautifulSoup(FutHead.text, 'html.parser')

    Players = bs.findAll('div', {'class': 'content player-item font-24'})
    print("PLAYER COUNT IN PAGE: ", len(Players))
    for player in Players:
        name = player.findAll('span', {'class': 'player-name'})[0].get_text()

        nationality_key = player.findAll("img", {"class": "player-nation"})[0]["data-src"]
        nationality = get_nationality_from_cache(nationality_key)
        if nationality is None:
            nationality = get_nationality(player)
            nationality_cache[nationality_key] = nationality
            print(f"Cache set for {nationality}")
        rating = player.findAll('span', {'class': re.compile('revision-gradient shadowed font-12')})[0].get_text()

        # Stats
        stats = player.findAll('span', {'class': "player-stat stream-col-60 hidden-md hidden-sm"})
        pace = stats[0].findAll('span', {'class': 'value'})[0].get_text()
        shooting = stats[1].findAll('span', {'class': 'value'})[0].get_text()
        passing = stats[2].findAll('span', {'class': 'value'})[0].get_text()
        dribbling = stats[3].findAll('span', {'class': 'value'})[0].get_text()
        defending = stats[4].findAll('span', {'class': 'value'})[0].get_text()
        physical = stats[5].findAll('span', {'class': 'value'})[0].get_text()

        players.append([name, nationality, rating, pace, shooting, passing, dribbling, defending, physical])

    print('page ' + str(page) + ' is done!')

df_cols = ["NAME", "NATIONALITY", "RATING", "PACE","SHOOTING","PASSING","DRIBBLING","DEFENDING","PHYSICAL"]

player_df = pd.DataFrame(players,  columns=df_cols)
player_df.to_csv(f"FIFA{key}.csv")


# Runtime end
print(time.clock() - start)