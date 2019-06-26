#!~/anaconda3/bin/R
#
###########################################
#
# File: Fanning_the_Flames_R.R
# Author: Ra Inta
# Description:
# Created: June 24, 2019
# Last Modified: June 25, 2019, R.I.
#
###########################################

# What is our current working directory?
getwd()

##################################################
### 1: Importing data
##################################################

#install.packages("RSQLite", repos="https://cran.revolutionanalytics.com/")
library("RSQLite")

# Connect to the user database (here, a SQLite DB) 
con <- RSQLite::dbConnect(drv=RSQLite::SQLite(), dbname="../data/user_data.sql")

# List the tables
dbListTables(con)

# Import user information to a data.frame
useRs_df <- dbGetQuery(con, 'SELECT * FROM user_accounts')

# count the users
dbGetQuery(con,'SELECT COUNT(*) FROM user_accounts' )

# Get the account balances of users over the age of 30:
account_over30 <- dbGetQuery(con, "SELECT account_balance, user_id FROM user_accounts WHERE age > 30") 
head(account_over30)

# Yahoo have kindly offered a cross-promotion for our users.
# Select the users with a Yahoo email address:
yahoo_users <- dbGetQuery(con, "SELECT * FROM user_accounts WHERE email LIKE '%yahoo%'")

head(yahoo_users[c('first_name', 'last_name', 'email')])

# Always a good policy to close your DB connection ASAP.
dbDisconnect(con)


#install.packages("readxl")

# The marketing people have the campaign stored in an Excel spreadsheet.
library("readxl")
campaign_df <- read_excel("../data/advertising_campaign.xlsx")
campaign_df

##################################################
### 2: Exploratory Data Analysis I
##################################################

# We'll first look at the most important information: the users

# Size of the dataset
dim(useRs_df)

# Names of columns:
names(useRs_df)

# Quick look at the first few rows:
head(useRs_df)

# Access the age column only:
head(useRs_df$age, 10)

# Alternatively:
head(useRs_df["age"], 10)

# Get a neat summary of each column, including data types etc.
str(useRs_df)

# Get some descriptive statistics for the numerical data:
summary(useRs_df)

# Alternatively:
#install.packages("Hmisc")
library("Hmisc")
describe(useRs_df)

# Univariate description of account balances:
hist(useRs_df$account_balance)

# Brutal! Perhaps, like many resource distributions, this is a Pareto distribution:
useRs_df$log_account_balance <- log10(useRs_df$account_balance + 1)
hist(useRs_df$log_account_balance)


# Quantify the missingness:
sum(is.na(useRs_df))  # 2195
summary(is.na(useRs_df))

# We don't need the address column:
useRs_df$address <- NULL

# We could change the default value of missing gender:
useRs_df[is.na(useRs_df)] <- "Unknown"
sample(useRs_df, 5)

describe(useRs_df)


sum(is.na(useRs_df$gender))  #  None

# Get dupes:
sum(duplicated(useRs_df))
dim(unique(useRs_df))

# Drop duplicates
useRs_df <- unique(useRs_df)

# Merge the user data and the corresponding advertising campaign data
library("dplyr")
data_df <- merge(x=useRs_df, y=campaign_df, by="user_id", all.x=TRUE)

dim(data_df)
names(data_df)
sum(duplicated(useRs_df))
sum(is.na(useRs_df))

##################################################
### 3: Visualization
##################################################

#install.packages("GGally")
library("GGally")

ggpairs(data_df[c("account_balance", "age", "marketing_level", "sales")])

data_df$log_sales <- log10(data_df$sales + 1)
hist(data_df$log_sales)

ggpairs(data_df[c("log_account_balance", "age", "marketing_level", "log_sales")])

##################################################
### 4: Exploratory Data Analysis II and hypothesis testing
##################################################


# Does the marketing level have any effect on sales?
data_df %>% 
    group_by(marketing_level) %>%
    summarise(mean_sales=mean(sales))

# Looks like its linear!


# Upon discussion, marketing finally(!) let us know that their advertising campaign was 
# targeted at customers between the ages of 25 and 35. Was this campaign effective?

data_df$age_demographic <- as.factor(ifelse(data_df$age >= 25 & data_df$age <=35, "yes", "no"))

data_df %>% 
    group_by(age_demographic) %>%
    summarise(mean_sales=mean(sales))

# It appears so!
library(ggplot2)
ggplot(data_df, aes(y=sales, x=factor(age_demographic))) + geom_boxplot()

# OK, looks like we're swamped by outliers. Time for the log-transformed version:

ggplot(data_df, aes(y=log_sales, x=factor(age_demographic))) + geom_boxplot()

# Nice.

t.test(sales ~ age_demographic, data=data_df, var.equal=TRUE)

# As expected: highly significant

xtabs(age_demographic ~ factor(marketing_level), data=data_df) 

cor.test( ~ account_balance + sales, data=data_df)

##################################################
### 5: Linear Regression
##################################################

# Single factor: account balance
mod0 <- lm(sales ~ account_balance, data=data_df) 

summary(mod0) 

plot(data_df$account_balance, data_df$sales, main="Sales by account balance") 

abline(mod0, col="red") 

hist(residuals(mod0))

# Check the effect of age demographic on sales
modDemographic <- lm(sales ~ age_demographic, data=data_df) 
summary(modDemographic) 


# Single factor: age
mod1 <- lm(sales ~ age, data=data_df) 

summary(mod1) 

plot(data_df$age, data_df$sales, main="Sales by customer age") 

abline(mod1, col="red") 

hist(residuals(mod1))

# Polynomial in age 
mod1b <- lm(sales ~ age + I(age**2), data=data_df) 

summary(mod1b) 

plot(data_df$age, data_df$sales, main="Sales by customer age") 

abline(mod1b, col="red") 

hist(residuals(mod1b))

# Clues for multilinear regression
#install.packages("car", repos="https://cran.revolutionanalytics.com/")
library(car) 

scatterplotMatrix(data_df[c('sales', 'account_balance', 'age', 'marketing_level')],
                  spread=FALSE, 
                  lty.smooth=2,
                  main="Scatter Plot Matrix") 

mod2 <- lm(sales ~ age + I(age**2) + age_demographic + marketing_level + account_balance, data=data_df) 
summary(mod2) 

mod3 <- lm(sales ~ age + I(age**2) + marketing_level:age_demographic + account_balance, data=data_df) 
 
summary(mod3) 


# Prediction
pred_df <- expand.grid("age"=seq(16, 65, 5), 
              "age_demographic"=c("yes","no"), 
              "account_balance"=seq(0, 1000, 10), 
              "marketing_level"=1:10 ) 

## Predict new results 
pred_df$sales_pred <- predict(mod3, pred_df) 
library(ggplot2)

## visualize these results 
ggplot(pred_df, aes(x=marketing_level, y=sales_pred, color=age_demographic, alpha=0.5)) + geom_point() 

plot(mod3) 

#install.packages("gvlma", repos="https://cran.revolutionanalytics.com/")
library(gvlma) 

gvmod3 <- gvlma(mod3) 
summary(gvmod3) 

mod4 <- lm(sales ~ age + I(age**2) + marketing_level:age_demographic, data=data_df) 

mod5 <- lm(sales ~ I(age**2) + marketing_level:age_demographic, data=data_df) 

anova(mod5, mod4) 

AIC(mod0, mod1, mod2, mod3, mod4, mod5) 

library(MASS) 
mod6 <- lm(sales ~ age + I(age**2) + marketing_level:age_demographic + account_balance, data=data_df) 

stepAIC(mod6, direction="backward") 


###########################################
### End of Fanning_the_Flames_R.R
###########################################
