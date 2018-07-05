library(vars)
library(readr)
library(ggplot2)
library(dplyr)
library(lubridate)
library(xts)
library(broom)
library(xtable)
library(stringr)
library(tseries)
library(lmtest)
library(reshape2)

# Match features
wc_match_results <- read_csv("results.csv")

# Remove old games
wc_match_results <- wc_match_results %>% filter(date > as.Date("1980-01-01"))

countries <- union(wc_match_results$home_team, wc_match_results$away_team)
goals_between_countries <- data.frame(matrix(ncol = length(countries), nrow = length(countries)))
colnames(goals_between_countries) <- countries


for (i in 1:length(countries)) {
  for (j in 1:length(countries)) {
    home <- countries[i]
    opponent <- countries[j]
    
    goals <- wc_match_results %>%
      filter((home_team == home | away_team == home) & (home_team == opponent | away_team == opponent)) %>%
      summarise(home_goals = sum(if_else(home_team == home, home_score, away_score)),
                away_goals = sum(if_else(home_team == opponent, home_score, away_score)))
    
    goals_between_countries[i, j] <- (goals$home_goals - goals$away_goals)/(goals$home_goals +goals$away_goals)
  }
}
