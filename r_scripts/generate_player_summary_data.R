library(readr)
library(dplyr)
library(lubridate)
library(broom)
library(reshape2)
library(ggplot2)

player_attributes <- read_csv("../data/generated/sofifa_player_attributes.csv")
player_attributes <- player_attributes[,2:ncol(player_attributes)]

top <- 3
half <- 5
whole <- 10
GK <- 2

summary = player_attributes %>%
  group_by(nationality, year) %>%
  filter(n() > 23) %>%
  do(head(., 23)) %>%
  summarise(
    overall_rating_max = max(overall_rating),
    overall_rating_min = min(overall_rating),
    overall_rating_avg = mean(overall_rating),
    potential_max = max(potential),
    potential_min = min(potential),
    potential_avg = mean(potential),
    height = mean(height),
    weight = mean(weight),
    age = mean(age),
    top_11_age = mean(head(age, 11)),
    weak_foot = mean(weak_foot),
    international_reputation = mean(international_reputation),
    Crossing = mean(head(sort(Crossing, decreasing = TRUE), half)),
    Finishing = mean(head(sort(Finishing, decreasing = TRUE), half)),
    Heading_Accuracy = mean(head(sort(Heading_Accuracy, decreasing = TRUE), half)),
    Short_Passing = mean(head(sort(Short_Passing, decreasing = TRUE), half)),
    Dribbling = mean(head(sort(Dribbling, decreasing = TRUE), half)),
    FK_Accuracy = mean(head(sort(FK_Accuracy, decreasing = TRUE), top)),
    Long_Passing = mean(head(sort(Long_Passing, decreasing = TRUE), half)),
    Ball_Control = mean(head(sort(Ball_Control, decreasing = TRUE), half)),
    Acceleration = mean(head(sort(Acceleration, decreasing = TRUE), half)),
    Sprint_Speed = mean(head(sort(Sprint_Speed, decreasing = TRUE), top)),
    Reactions = mean(head(sort(Reactions, decreasing = TRUE), half)),
    Shot_Power = mean(head(sort(Shot_Power, decreasing = TRUE), half)),
    Stamina = mean(head(sort(Stamina, decreasing = TRUE), whole)),
    Strength = mean(head(sort(Strength, decreasing = TRUE), whole)),
    Long_Shots = mean(head(sort(Long_Shots, decreasing = TRUE), top)),
    Aggression = mean(head(sort(Aggression, decreasing = TRUE), half)),
    Penalties = mean(head(sort(Penalties, decreasing = TRUE), top)),
    Marking = mean(head(sort(Marking, decreasing = TRUE), top)),
    Standing_Tackle = mean(head(sort(Standing_Tackle, decreasing = TRUE), half)),
    GK_Diving = mean(head(sort(GK_Diving, decreasing = TRUE), GK)),
    GK_Handling = mean(head(sort(GK_Handling, decreasing = TRUE), GK)),
    GK_Kicking = mean(head(sort(GK_Kicking, decreasing = TRUE), GK)),
    GK_Positioning = mean(head(sort(GK_Positioning, decreasing = TRUE), GK)),
    GK_Reflexes = mean(head(sort(GK_Reflexes, decreasing = TRUE), GK)))


r_coef <- 0.90
summary_shit_teams = player_attributes %>%
  group_by(nationality, year) %>%
  filter(n() < 23) %>%
  do(head(., 23)) %>%
  summarise(
    overall_rating_max = max(overall_rating),
    overall_rating_min = min(overall_rating),
    overall_rating_avg = mean(overall_rating) * min(1, max(n()/18, r_coef)),
    potential_max = max(potential),
    potential_min = min(potential),
    potential_avg = mean(potential) * min(1, max(n()/18, r_coef)),
    height = mean(height) * min(1, max(n()/18, r_coef)),
    weight = mean(weight) * min(1, max(n()/18, r_coef)),
    age = mean(age) * min(1, max(n()/18, r_coef)),
    top_11_age = mean(head(age, 11)) * min(1, max(n()/11, r_coef)),
    weak_foot = mean(weak_foot) * min(1, max(n()/18, r_coef)),
    international_reputation = mean(international_reputation) * min(1, max(n()/18, r_coef)),
    Crossing = mean(head(sort(Crossing, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Finishing = mean(head(sort(Finishing, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Heading_Accuracy = mean(head(sort(Heading_Accuracy, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Short_Passing = mean(head(sort(Short_Passing, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Dribbling = mean(head(sort(Dribbling, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    FK_Accuracy = mean(head(sort(FK_Accuracy, decreasing = TRUE), top)) * min(1, max(n()/top, r_coef)),
    Long_Passing = mean(head(sort(Long_Passing, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Ball_Control = mean(head(sort(Ball_Control, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Acceleration = mean(head(sort(Acceleration, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Sprint_Speed = mean(head(sort(Sprint_Speed, decreasing = TRUE), top)) * min(1, max(n()/top, r_coef)),
    Reactions = mean(head(sort(Reactions, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Shot_Power = mean(head(sort(Shot_Power, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Stamina = mean(head(sort(Stamina, decreasing = TRUE), whole)) * min(1, max(n()/whole, r_coef)),
    Strength = mean(head(sort(Strength, decreasing = TRUE), whole)) * min(1, max(n()/whole, r_coef)),
    Long_Shots = mean(head(sort(Long_Shots, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Aggression = mean(head(sort(Aggression, decreasing = TRUE), half)) * min(1, max(n()/half, r_coef)),
    Penalties = mean(head(sort(Penalties, decreasing = TRUE), top)) * min(1, max(n()/top, r_coef)),
    Marking = mean(head(sort(Marking, decreasing = TRUE), top)) * min(1, max(n()/top, r_coef)),
    Standing_Tackle = mean(head(sort(Standing_Tackle, decreasing = TRUE), half)) * min(1, max(n()/top, r_coef)),
    GK_Diving = mean(head(sort(GK_Diving, decreasing = TRUE), GK)),
    GK_Handling = mean(head(sort(GK_Handling, decreasing = TRUE), GK)),
    GK_Kicking = mean(head(sort(GK_Kicking, decreasing = TRUE), GK)),
    GK_Positioning = mean(head(sort(GK_Positioning, decreasing = TRUE), GK)),
    GK_Reflexes = mean(head(sort(GK_Reflexes, decreasing = TRUE), GK)))

summary <- rbind(summary, summary_shit_teams)

summary$nationality[summary$nationality == "Bosnia Herzegovina"] <- "Bosnia and Herzegovina"
summary$nationality[summary$nationality == "Republic of Ireland"] <- "Ireland"
summary$nationality[summary$nationality == "Central African Rep."] <- "Central African Republic"
summary$nationality[summary$nationality == "DR Congo"] <- "Congo DR"
summary$nationality[summary$nationality == "Guinea Bissau"] <- "Guinea-Bissau"
summary$nationality[summary$nationality == "Trinidad & Tobago"] <- "Trinidad and Tobago"
summary$nationality[summary$nationality == "Yemen"] <- "Yemen DPR"
summary$nationality[summary$nationality == "Iran"] <- "IR Iran"
write.csv(summary, file = "data/generated/team_level_player_data.csv")


