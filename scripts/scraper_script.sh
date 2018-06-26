#!/bin/bash

years='07 08 09 10 11 12'
for year in $years
do
    echo $year
    python sofifa_extensive_player_scraper.py --year $year
    sleep 10s
done
echo "All done"