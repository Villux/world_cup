library(readr)

matches <- read_csv('results.csv')
ranking <- read_csv('fifa_ranking.csv')
player <- read_csv('player_ranks_summary.csv')

all_teams <- union(union(ranking$country_full, player$NATIONALITY), union(matches$home_team, matches$away_team))
intersect_teams <- intersect(intersect(ranking$country_full, player$NATIONALITY), intersect(matches$home_team, matches$away_team))

not_in_all <- setdiff(all_teams, intersect_teams)
