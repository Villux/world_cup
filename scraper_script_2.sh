#!/bin/bash

years='13 14 15 16 17 18'
for year in $years
do
    echo $year
    python sofifa_extensive_player_scraper.py --year $year
    sleep 10s
done
echo "All done"