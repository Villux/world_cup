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
elo_rankings <- read_csv("elo_ranking.csv")
elo_rankings <- elo_rankings[,2:ncol(elo_rankings)]

# Merge datasets for home team
wc_match_results <- merge(x = wc_match_results, y = elo_rankings,
              by.x = c("date", "home_team"),
              by.y = c("date", "team"))
names(wc_match_results)[ncol(wc_match_results)] <- "home_elo"

wc_match_results <- merge(x = wc_match_results, y = elo_rankings,
                          by.x = c("date", "away_team"),
                          by.y = c("date", "team"))
names(wc_match_results)[ncol(wc_match_results)] <- "away_elo"

# Elo diff
wc_match_results$elo_diff <- wc_match_results$home_elo -wc_match_results$away_elo

# Goals difference
wc_match_results$score_difference <- wc_match_results$home_score - wc_match_results$away_score

# Mean Goal difference in previous matches
score_diff_lag <- 10
wc_match_results <- wc_match_results %>% 
  group_by(home_team) %>%
  mutate(home_score_difference_lag = lag(score_difference, 1)) %>%
  mutate(home_avg_goal_diff = rollapply(data = home_score_difference_lag, 
                                        width = score_diff_lag, 
                                        FUN = mean, 
                                        align = "right", 
                                        fill = NA, 
                                        na.rm = T)) %>%
  ungroup()

wc_match_results <- wc_match_results %>% 
  group_by(away_team) %>%
  mutate(away_score_difference_lag = lag(score_difference, 1)) %>%
  mutate(away_avg_goal_diff = rollapply(data = away_score_difference_lag, 
                                        width = score_diff_lag, 
                                        FUN = mean, 
                                        align = "right", 
                                        fill = NA, 
                                        na.rm = T)) %>%
  ungroup()

# Mean goals received by the opposing team
wc_match_results <- wc_match_results %>% 
  group_by(home_team) %>%
  mutate(avg_goals_received = rollapply(data = away_score, 
                                        width = score_diff_lag, 
                                        FUN = mean, 
                                        align = "right", 
                                        fill = NA, 
                                        na.rm = T)) %>%
  ungroup()



wc_match_results <- wc_match_results %>%
  group_by(home_team) %>%
  tidyr::fill(home_avg_goal_diff, home_score_difference_lag) %>%
  arrange(date)

wc_match_results <- wc_match_results %>%
  group_by(away_team) %>%
  tidyr::fill(away_avg_goal_diff, away_score_difference_lag) %>%
  arrange(date)

wc_match_results <- wc_match_results %>%
  group_by(home_team) %>%
  tidyr::fill(avg_goals_received) %>%
  arrange(date)

wc_match_results$home_avg_goal_diff[is.na(wc_match_results$home_avg_goal_diff)] <- 0
wc_match_results$away_avg_goal_diff[is.na(wc_match_results$away_avg_goal_diff)] <- 0
wc_match_results$home_score_difference_lag[is.na(wc_match_results$home_score_difference_lag)] <- 0
wc_match_results$away_score_difference_lag[is.na(wc_match_results$away_score_difference_lag)] <- 0
wc_match_results$avg_goals_received[is.na(wc_match_results$avg_goals_received)] <- 0

# Win, draw or lose: [1, 0, -1]
wc_match_results$home_win <- sign(wc_match_results$score_difference)

# Previous world cup wins
world_cup_wins <- wc_match_results %>% 
  filter(tournament == "FIFA World Cup") %>%
  group_by(home_team) %>%
  mutate(wc_home_wins = cumsum(home_win)) %>%
  ungroup() %>%
  group_by(away_team) %>%
  mutate(wc_away_wins = -cumsum(home_win)) %>%
  ungroup() %>%
  select("date", "home_team", "wc_home_wins", "wc_away_wins")

wc_match_results <- merge(x = wc_match_results, y = world_cup_wins, by=c("date", "home_team"), all.x = TRUE)
wc_match_results <- wc_match_results %>%
  group_by(home_team) %>%
  tidyr::fill(wc_home_wins) %>%
  arrange(date) %>%
  group_by(away_team) %>%
  tidyr::fill(wc_away_wins) %>%
  arrange(date)

wc_match_results$wc_home_wins[is.na(wc_match_results$wc_home_wins)] <- 0
wc_match_results$wc_away_wins[is.na(wc_match_results$wc_away_wins)] <- 0


fifa_rankings <- read_csv("daily_fifa_ranking.csv") 
fifa_rankings <- fifa_rankings[,2:ncol(fifa_rankings)]

wc_dates <- unique(wc_match_results$date)
fifa_rankings <- fifa_rankings %>% filter(as.Date(date) %in% wc_dates)


# Merge datasets for home team
data <- merge(x = wc_match_results, y = fifa_rankings,
              by.x = c("date", "home_team"),
              by.y = c("date", "country"),
              all.x = TRUE)

col_range <- (ncol(wc_match_results)+1):ncol(data)
# Prefix columns
names(data)[col_range] <- paste("home", colnames(data)[col_range], sep = "_")

# Merge datasets for away team
data <- merge(x = data, y = fifa_rankings,
              by.x = c("date", "away_team"),
              by.y = c("date", "country"),
              all.x = TRUE)
col_range <- (tail(col_range, 1)+1):ncol(data)
names(data)[col_range] <- paste("away", colnames(data)[col_range], sep = "_")

# Rank diff
data$home_rank <- as.numeric(as.character(data$home_rank))
data$away_rank <- as.numeric(as.character(data$away_rank))
data$home_cur_year_avg <- as.numeric(as.character(data$home_cur_year_avg))
data$away_cur_year_avg <- as.numeric(as.character(data$away_cur_year_avg))
data$rank_diff <- data$home_rank - data$away_rank
data$rank_diff_avg <- data$home_cur_year_avg - data$away_cur_year_avg

# Keep only complete
data <- data[complete.cases(data),]

write.csv(data, file = "dataset.csv")




