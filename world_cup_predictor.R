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
library(randomForest)
library(caret)
library(party)
library(xgboost)
library(class)

results <- read_csv("dataset.csv")
results <- results[,2:ncol(results)]

train <- results %>% 
  filter(year(date) < 2017)

test <- results %>% 
  filter(year(date) >= 2017)


# Random forest regression
rfr <- randomForest((home_score - away_score) ~ rank_diff  + home_avg_goal_diff + away_avg_goal_diff + 
                      home_score_difference_lag + away_score_difference_lag, data=train, ntree = 10)
varImpPlot(rfr)
rfr_prediction <- predict(rfr, test)
rfr_prediction.round <- round(rfr_prediction)
rfr_prediction.real <- test$home_score - test$away_score 
rfr_prediction.accuracy <- sum(rfr_prediction.real == rfr_prediction.round)/nrow(test)

# Fancy randon forest
crfr <- cforest((home_score - away_score) ~ rank_diff  + home_avg_goal_diff + away_avg_goal_diff + 
                 home_score_difference_lag + away_score_difference_lag,
               data = train, 
               controls=cforest_unbiased(ntree=10, mtry=3))
crfr_prediction <- predict(crfr, test, OOB=TRUE, type = "response")
crfr_prediction.round <- round(crfr_prediction)
crfr_prediction.real <- test$home_score - test$away_score 
crfr_prediction.accuracy <- sum(crfr_prediction.real == crfr_prediction.round)/nrow(test)

# Linear regression accuracy
lmr <- lm((home_score - away_score) ~ rank_diff  + home_avg_goal_diff + away_avg_goal_diff + 
     home_score_difference_lag + away_score_difference_lag, train)
summary(lmr)

lmr_prediction <- predict(lmr, test)
lmr_prediction.round <- round(lmr_prediction)
lmr_prediction.real <- test$home_score - test$away_score 
lmr_prediction.accuracy <- sum(lmr_prediction.real == lmr_prediction.round)/nrow(test)

hist(lmr_prediction.real - lmr_prediction.round, 50)


#Classification
train$home_win <- factor(train$home_win)

train.classification <- select(train, "rank_diff", "home_avg_goal_diff",
                               "away_avg_goal_diff", "home_score_difference_lag",
                               "away_score_difference_lag")

test.classification <- select(test, "rank_diff", "home_avg_goal_diff",
                              "away_avg_goal_diff", "home_score_difference_lag",
                              "away_score_difference_lag")

rfc <- randomForest(home_win ~ ., data=train.classification, ntree = 100)
var.imp = data.frame(importance(rfc, type=2))

rfc_prediction <- predict(rfc, test)
rfc_prediction.accuracy <- sum(rfc_prediction == test.classification$home_win)/nrow(test)


#KNN
prc_test_pred <- knn(train = train.classification, test = test.classification, cl = train$home_win, k=100)
prc_test_pred.accuracy <- sum(prc_test_pred == test$home_win)/nrow(test)
