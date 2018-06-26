#!/bin/bash

years='07 08 09 10 11 12 13 14 15 16 17 18'
for year in $years
do
    echo $year
    python sofifa_national_team_scraper.py --year $year
    sleep 10s
done
echo "All done"