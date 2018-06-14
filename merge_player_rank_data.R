library(readr)
library(dplyr)
library(lubridate)
library(broom)
library(reshape2)

player_summaries <- read_csv("player_ranks_summary.csv")
player_summaries <- player_summaries[,2:ncol(player_summaries)]

match_data <- read_csv("dataset.csv")
match_data <- match_data[,2:ncol(match_data)]
match_data$year <- year(match_data$date)

data <- merge(match_data, player_summaries, by.x = c("year", "home_team"), by.y = c("year", "NATIONALITY"), all.x = TRUE)
col_range <- (ncol(match_data)+1):ncol(data)
# Prefix columns
names(data)[col_range] <- paste("home", colnames(data)[col_range], sep = "_")

data <- merge(data, player_summaries, by.x = c("year", "away_team"), by.y = c("year", "NATIONALITY"), all.x = TRUE)
col_range <- (tail(col_range, 1)+1):ncol(data)
# Prefix columns
names(data)[col_range] <- paste("away", colnames(data)[col_range], sep = "_")

data[is.na(data)] <- 0

data$rating_diff <- data$home_rating - data$away_rating
data$pace_diff <- data$home_pace - data$away_pace
data$shooting_diff <- data$home_shooting - data$away_shooting
data$passing_diff <- data$home_passing - data$away_passing
data$dribbling_diff <- data$home_dribbling - data$away_dribbling
data$defending_diff <- data$home_defending - data$away_defending
data$physical_diff <- data$home_physical - data$away_physical

write.csv(data, file = "dataset_player_rating.csv")


master_data <- data

independent_vars <- c("home_rank", "away_rank", "home_elo", "away_elo", "home_avg_goal_diff", "away_avg_goal_diff", "avg_goals_received")
dependent_vars <- c("home_rating", "home_pace", "home_shooting", "home_passing", "home_dribbling", "home_defending", "home_physical",
                    "away_rating", "away_pace", "away_shooting", "away_passing", "away_dribbling", "away_defending", "away_physical")

for (d_var in dependent_vars) {
  train <- master_data %>% filter(UQ(as.name(d_var)) > 0)
  predict_data <- master_data %>% filter(UQ(as.name(d_var)) == 0)
  fit <- lm(reformulate(termlabels = independent_vars, response = d_var), train)
  master_data[master_data[d_var] == 0,][d_var] <- predict(fit, predict_data)
}

data <- master_data

data$rating_diff <- data$home_rating - data$away_rating
data$pace_diff <- data$home_pace - data$away_pace
data$shooting_diff <- data$home_shooting - data$away_shooting
data$passing_diff <- data$home_passing - data$away_passing
data$dribbling_diff <- data$home_dribbling - data$away_dribbling
data$defending_diff <- data$home_defending - data$away_defending
data$physical_diff <- data$home_physical - data$away_physical

write.csv(data, file = "dataset_player_rating_augmented.csv")
