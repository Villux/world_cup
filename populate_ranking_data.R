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

fifa_rankings <- read_csv("fifa_ranking.csv")
fifa_rankings$rank <- as.numeric(as.character(fifa_rankings$rank))

start_date <- min(fifa_rankings$rank_date)
end_date <- max(fifa_rankings$rank_date)
daily_country <- data.frame(matrix(ncol = ncol(fifa_rankings), nrow = 0))
names(daily_country) <- colnames(fifa_rankings)
countries <- unique(fifa_rankings$country_full)
for (country in countries){
  tmp <- data.frame(
    date = seq(start_date, end_date, by = "1 day"),
    country = country
  )
  daily_country <- rbind(daily_country, tmp)
}

fifa_rankings <- merge(x = daily_country, 
                       y = fifa_rankings, 
                       by.x = c("date", "country"), 
                       by.y = c("rank_date", "country_full"), 
                       all.x = TRUE)

filled <- fifa_rankings %>% group_by(country) %>% do(na.locf(.))

write.csv(filled, file = "daily_fifa_ranking.csv")

