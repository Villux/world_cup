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
      pace = mean(head(sort(PACE, decreasing = TRUE), 6)),
      shooting = mean(head(sort(SHOOTING, decreasing = TRUE), 5)),
      passing = mean(head(sort(PASSING, decreasing = TRUE), 10)),
      dribbling = mean(head(sort(DRIBBLING, decreasing = TRUE), 5)),
      defending = mean(head(sort(DEFENDING, decreasing = TRUE), 5)),
      physical = mean(head(sort(PHYSICAL, decreasing = TRUE), 8)),
      year = year)
  
  summary_shit_teams = player_stats %>% 
    group_by(NATIONALITY) %>%
    filter(n() < 23) %>%
    do(head(., 23)) %>%
    summarise(
      rating = mean(RATING) * 0.8,
      pace = mean(RATING) * 0.8,
      shooting = mean(RATING)* 0.8,
      passing = mean(RATING)* 0.8,
      dribbling = mean(RATING)* 0.8,
      defending = mean(RATING)* 0.8,
      physical = mean(RATING)* 0.8,
      year = year)
  year <- year + 1
  
  summary <- rbind(summary, summary_shit_teams)
  summary_data <- rbind(summary_data, summary)
}

write.csv(summary_data, file = "player_ranks_summary.csv")
