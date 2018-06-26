library(readr)
library(ggplot2)
library(dplyr)
library(lubridate)
library(broom)
library(xtable)
library(stringr)
library(tseries)

match_results <- read_csv("results.csv")

afc_tournaments <- c("AFC Asian Cup", "AFC Asian Cup qualification", "AFC Challenge Cup", "AFC Challenge Cup qualification")
caf_tournaments <- c("African Cup of Nations", "African Cup of Nations qualification",
                     "West African Cup", "African Nations Championship", "CECAFA Cup") 
concacaf_tournaments <- c("Gold Cup", "Gold Cup qualification", "CONCACAF Championship", "CONCACAF Championship qualification")
conmebol_tournaments <- c("Copa America")
ofc_tournaments <- c("Oceania Nations Cup", "Oceania Nations Cup qualification")

uefa_tournaments <- c("UEFA Euro qualification", "UEFA Euro")

confederations <- c("AFC", "CAF", "CONCACAF", "CONMEBOL", "OFC", "UEFA")
tournaments <- c(afc_tournaments, caf_tournaments, concacaf_tournaments, conmebol_tournaments, ofc_tournaments, uefa_tournaments)

conf_df <- data.frame(matrix(nrow = 0, ncol = 2))
names(conf_df) <- c("country", "confederation")

for (idx in 1:length(confederations)) {
  tmp <- match_results %>% 
    filter(tournament == tournaments[idx]) %>% 
    mutate(confederation = confederations[idx]) %>%
    select(country, confederation) %>%
    distinct(.)
  conf_df <- rbind(conf_df, tmp)
}


