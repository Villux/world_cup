library(readr)
library(dplyr)
library(lubridate)
library(broom)
library(reshape2)

data <- read_csv("FIFA10.csv")
summary_data <- data.frame(matrix(ncol = ncol(data), nrow = 0))
colnames(summary_data) <- colnames(data)

files <- c('FIFA10.csv', 'FIFA11.csv', 'FIFA12.csv', 'FIFA13.csv', 'FIFA14.csv',
           'FIFA15.csv', 'FIFA16.csv', 'FIFA17.csv', 'FIFA18.csv')
year <- 2010
for (file in files){
  player_stats <- read_csv(file)
  player_stats <- player_stats[,2:ncol(player_stats)]
  player_stats <- player_stats[!duplicated(player_stats$NAME),]
  summary = player_stats %>% 
    group_by(NATIONALITY) %>%
    filter(n() > 23) %>%
    do(head(., 23)) %>%
    summarise(
      rating = mean(RATING),
      rating_max = max(RATING),
      rating_min = min(RATING),
      pace = mean(head(sort(PACE, decreasing = TRUE), 6)),
      pace_max = max(PACE),
      pace_min = min(PACE),
      shooting = mean(head(sort(SHOOTING, decreasing = TRUE), 5)),
      shooting_max = max(SHOOTING), 
      shooting_min = min(SHOOTING),
      passing = mean(head(sort(PASSING, decreasing = TRUE), 10)),
      passing_max = max(PASSING),
      passing_min = min(PASSING),
      dribbling = mean(head(sort(DRIBBLING, decreasing = TRUE), 5)),
      dribbling_max = max(DRIBBLING),
      dribbling_min = min(DRIBBLING),
      defending = mean(head(sort(DEFENDING, decreasing = TRUE), 5)),
      defending_max = max(DEFENDING),
      defending_min = min(DEFENDING),
      physical = mean(head(sort(PHYSICAL, decreasing = TRUE), 8)),
      physical_max = max(PHYSICAL),
      physical_min = min(PHYSICAL),
      year = year)
  
  r_coef <- 0.90
  summary_shit_teams = player_stats %>% 
    group_by(NATIONALITY) %>%
    filter(n() < 23) %>%
    do(head(., 23)) %>%
    summarise(
      rating = mean(RATING) * min(1, max(n()/18, r_coef)),
      rating_max = max(RATING),
      rating_min = min(RATING),
      pace = mean(RATING) * min(1, max(n()/18, r_coef)),
      pace_max = max(PACE),
      pace_min = min(PACE),
      shooting = mean(SHOOTING)* min(1, max(n()/18, r_coef)),
      shooting_max = max(SHOOTING),
      shooting_min = min(SHOOTING),
      passing = mean(PASSING)* min(1, max(n()/18, r_coef)),
      passing_max = max(PASSING),
      passing_min = min(PASSING),
      dribbling = mean(DRIBBLING)* min(1, max(n()/18, r_coef)),
      dribbling_max = max(DRIBBLING),
      dribbling_min = min(DRIBBLING),
      defending = mean(DEFENDING)* min(1, max(n()/18, r_coef)),
      defending_max = max(DEFENDING),
      defending_min = min(DEFENDING),
      physical = mean(RATING)* min(1, max(n()/18, r_coef)),
      physical_max = max(PHYSICAL),
      physical_min = min(PHYSICAL),
      year = year)
  year <- year + 1
  
  summary <- rbind(summary, summary_shit_teams)
  summary_data <- rbind(summary_data, summary)
}

write.csv(summary_data, file = "player_ranks_summary.csv")