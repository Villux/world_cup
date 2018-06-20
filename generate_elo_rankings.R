library(readr)
library(dplyr)
library(lubridate)
library(elo)

# Data
matches <- read_csv('results.csv')

# Elo rating table
teams <- data.frame(team = unique(c(matches$home_team, matches$away_team)))
teams <- teams %>%
  mutate(elo = 1500, date = as.Date('1872-11-30'))

# Game end results
matches <- matches %>%
  mutate(result = if_else(home_score > away_score, 1,
                          if_else(home_score == away_score, 0.5, 0)))

# Select only the needed columns
matches <- matches %>%
  select(date, home_team, away_team, result, date, tournament, home_score, away_score) %>%
  arrange(date)

for (i in seq_len(nrow(matches))) {
  match <- matches[i, ]
  
  # Pre-match ratings
  teamA_elo <- tail(subset(teams, team == match$home_team)$elo, 1)
  teamB_elo <- tail(subset(teams, team == match$away_team)$elo, 1)
  
  if (match$tournament %in% c("FIFA World Cup")) {
    K <- 60
  } else if (match$tournament %in% c("Confederations Cup",
                                     "Copa America",
                                     "UEFA Euro",
                                     "FIFA World Cup qualification"
                                     )) {
    
    K <- 50
  } else if (match$tournament %in% c("AFC Asian Cup",
                                     "Gold Cup",
                                     "CONCACAF Championship",
                                     "Oceania Nations Cup",
                                     "African Cup of Nations")) {
    K <- 50 * 0.85
  } else if (match$tournament %in% c("African Cup of Nations qualification", 
                                     "AFC Asian Cup qualification",
                                     "UEFA Euro qualification",
                                     "CONCACAF Championship qualification",
                                     "Oceania Nations Cup qualification",
                                     "AFC Challenge Cup",
                                     "AFC Challenge Cup qualification",
                                     "Gold Cup qualification"
                                     )) {
    K <- 40
  } else {
    K <- 30
  }
  
  score_diff <- abs(match$home_score - match$away_score)
  
  if (score_diff == 2) {
    K <- K * 1.5
  } else if (score_diff == 3) {
    K <- K * 1.75
  } else if (score_diff > 3) {
    K <- K * (1.75 + (score_diff-3)/8)
  }

  # Let's update our ratings
  new_elo <- elo.calc(wins.A = match$result,
                      elo.A = teamA_elo,
                      elo.B = teamB_elo,
                      k = K)
  
  # The results come back as a data.frame
  # with team A's new rating in row 1 / column 1
  # and team B's new rating in row 1 / column 2
  teamA_new_elo <- new_elo[1, 1]
  teamB_new_elo <- new_elo[1, 2]
  
  home_row <- data.frame(team = match$home_team, elo = teamA_new_elo, date = match$date)
  teams <- rbind(teams, home_row)
  
  away_row <- data.frame(team = match$away_team, elo = teamB_new_elo, date = match$date)
  teams <- rbind(teams, away_row)
}

write.csv(teams, file = "elo_ranking.csv")



