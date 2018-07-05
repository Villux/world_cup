library(readr)
library(dplyr)
library(lubridate)
library(broom)
library(reshape2)
library(tidyr)

# Fill missing columns with NaN
x.or.na <- function(x, df) if (x %in% names(df)) df[[x]] else NA

concat_df <- function(df, )

files <- c('SOFIFA_ext_07.csv', 'SOFIFA_ext_08.csv', 'SOFIFA_ext_09.csv', 'SOFIFA_ext_10.csv', 'SOFIFA_ext_11.csv', 
           'SOFIFA_ext_12.csv', 'SOFIFA_ext_13.csv', 'SOFIFA_ext_14.csv', 'SOFIFA_ext_15.csv', 'SOFIFA_ext_16.csv', 
           'SOFIFA_ext_17.csv', 'SOFIFA_ext_18.csv')

col_names <- colnames(read.csv('SOFIFA_ext_18.csv'))
col_names <- col_names[-1]
col_names <- c(col_names, "year")

all_player_data <- data.frame(matrix(nrow = 0, ncol = length(col_names)))
names(all_player_data) <- col_names
year <- 2007
for (file in files) {
  sofifa_year <- read_csv(file)
  sofifa_year <- sofifa_year[,2:ncol(sofifa_year)]
  sofifa_year$year <- year
  sofifa_year <- as.data.frame(Map(x.or.na, col_names, list(sofifa_year)))
  
  all_player_data <- rbind(all_player_data, sofifa_year)
  year <- year + 1
}

write.csv(all_player_data, "sofifa_player_attributes.csv")



