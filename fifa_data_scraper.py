import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np

def get_nationality(playerPage):
    link = playerPage.a["href"]
    page = requests.get('http://www.futhead.com/' + link)
    bs = BeautifulSoup(page.text, 'html.parser')
    return bs.findAll('div', {'class': 'player-sidebar-item'})[2].a.get_text()


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

for key, value in fifa.items():
    print('Doing Fifa ' + key)

    # List Intializations
    players = []
    attributes = []

    # Looping through all pages to retrieve players stats and information
    for page in range(1, 2):
        FutHead = requests.get('http://www.futhead.com/' + key + '/players/?page=' + str(page) + '&bin_platform=ps')
        bs = BeautifulSoup(FutHead.text, 'html.parser')
        Stats = bs.findAll('span', {'class': 'player-stat stream-col-60 hidden-md hidden-sm'})
        Names = bs.findAll('span', {'class': 'player-name'})
        Information = bs.findAll('span', {'class': 'player-club-league-name'})
        Ratings = bs.findAll('span', {'class': re.compile('revision-gradient shadowed font-12')})
        PlayerPages = bs.findAll('div', {'class': 'content player-item font-24'})

        # Calcualting the number of players per page
        num = len(bs.findAll('li', {'class': 'list-group-item list-group-table-row player-group-item dark-hover'}))

        # Parsing all players information
        for i in range(0, num):
            p = []
            p.append(Names[i].get_text())
            strong = Information[i].strong.extract()
            nationality = get_nationality(PlayerPages[i])
            try:
                p.append(re.sub('\s +', '', str(Information[i].get_text())).split('| ')[1])
            except IndexError:
                p.append((''))
            try:
                p.append(re.sub('\s +', '', str(Information[i].get_text())).split('| ')[2])
            except IndexError:
                p.append((''))
            p.append(strong.get_text())
            p.append(Ratings[i].get_text())
            p.append(nationality)
            players.append(p)

        # Parsing all players stats
        a = []
        for stat in Stats:
            if Stats.index(stat) % 6 == 0:
                if len(a) > 0:
                    attributes.append(a)
                a = []
            if stat.find('span', {'class': 'value'}) is None:
                pass
            else:
                a.append(stat.find('span', {'class': 'value'}).get_text())
        print('page ' + str(page) + ' is done!')

    df_cols = ["NAME","CLUB","LEAGUE","POSITION","RATING","NATIONALITY", "PACE","SHOOTING","PASSING","DRIBBLING","DEFENDING","PHYSICAL"]
    player_df = pd.DataFrame(np.hstack((players, attributes)), columns=df_cols)
    player_df.to_csv(f"{value}.csv")


# Runtime end
print(time.clock() - start)