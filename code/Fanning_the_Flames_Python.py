#!/usr/bin/env python
#
###########################################
#
# File: Fanning_the_Flames_Python.py
# Author: Ra Inta
# Description:
# Created: June 24, 2019
# Last Modified: June 25, 2019, R.I.
#
###########################################


import os
import sys
import pandas as pd
import numpy as np
import matplotlib as mpl
import seaborn as sns
import statsmodels as sm
os.getcwd()


print(f"System version: {textwrap.fill(sys.version)}\n")
print(f"Pandas version: {pd.__version__}\n")
print(f"Matplotlib version: {matplotlib.__version__}\n")
print(f"Numpy version: {np.__version__}\n")
print(f"Statsmodels version: {statsmodels.__version__}\n")

# Some housekeeping items for better interactivity with IPython
# and Jupyter:

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

pd.set_option('display.width', 80)
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 10

%matplotlib inline


##################################################
### 1: Importing data
##################################################

# Import module for handling database access.
import sqlite3

## import data

# Connect to the database
cnx = sqlite3.connect("../data/user_data.sql")

# The data are stored as two tables in the db:
users_df = pd.read_sql_query("SELECT * FROM user_accounts", cnx)

# Count number of user accounts
pd.read_sql_query('SELECT COUNT(*) FROM user_accounts', cnx)

# What are the account balances for customers over 30?
pd.read_sql_query(
    "SELECT account_balance, user_id FROM user_accounts WHERE age > 30 LIMIT 10",
    cnx)

# Yahoo have kindly offered a cross-promotion for our users.
# Select the users with a Yahoo email address:
yahoo_users = pd.read_sql_query(
    "SELECT * FROM user_accounts WHERE email LIKE '%yahoo%'", cnx)

yahoo_users[['first_name', 'last_name', 'email']].head()

# It's a good policy to close your db connection early as possible
cnx.close()

# The marketing people have the campaign stored in an Excel spreadsheet.
campaign_df = pd.read_excel("../data/advertising_campaign.xlsx")
campaign_df

##################################################
### 2: Exploratory Data Analysis I
##################################################

# We'll first look at the most important information: the users

# Size of the dataset
users_df.shape

# Names of columns:
users_df.columns.values

# Quick look at the first few rows:
users_df.head()

# Access the age column only:
users_df["age"].head(10)

# Alternatively:
users_df.loc[0:9, "age"]

# But NEVER:
users_df.age.head(10)

# Just. Don't. Even if you see it on StackOverflow

# Get the data types of each column
users_df.dtypes

# Get some descriptive statistics for the numerical data:
users_df.describe()

# Univariate description of account balances:
import matplotlib.pyplot as plt
plt.hist(users_df["account_balance"])

# Alternatively:
users_df["account_balance"].hist()

# Brutal! Perhaps, like many resource distributions, this is a Pareto distribution:
# We'll do some feature engineering and create a new column:
users_df["log_account_balance"] = np.log10(users_df["account_balance"] + 1)

users_df["log_account_balance"].hist(bins=20)

# Nice

sns.distplot(users_df["log_account_balance"])

# Even nicer.

# Quantify the missingness:
users_df.isnull().sum()  # 2195

# We don't need the address column:
del users_df["address"]

# Alternatively: pop off the queue
# users_df.pop("address")

users_df.columns.values

# We could change the default value of missing gender:
users_df["gender"].fillna("Unknown", inplace=True)

users_df["gender"].sample(5)

users_df["gender"].isnull().sum()  #  None

# Get dupes:
users_df.duplicated().sum()

# Drop duplicates
users_df.drop_duplicates(inplace=True)

# Merge the user data and the corresponding advertising campaign data

data_df = pd.merge(users_df, campaign_df, on="user_id", how="left")

data_df.shape
data_df.columns.values
data_df.duplicated().sum()
data_df.isnull().sum()

##################################################
### 3: Visualization
##################################################

ggpairs(data_df[c("account_balance", "age", "marketing_level", "sales")])

data_df["log_sales"] = np.log10(data_df["sales"] + 1)
data_df["log_sales"].hist(bins=20)

ggpairs(data_df[c("log_account_balance", "age", "marketing_level", "log_sales")])

from pandas.plotting import scatter_matrix
scatter_matrix(data_df[["log_account_balance", "age", "marketing_level", "log_sales"]])


##################################################
### 4: Exploratory Data Analysis II and hypothesis testing
##################################################


# Does the marketing level have any effect on sales?

data_df.groupby("age_demographic").mean()["sales"]

# Looks like its linear!


# Upon discussion, marketing finally(!) let us know that their advertising campaign was
# targeted at customers between the ages of 25 and 35. Was this campaign effective?

# Let's engineer that feature a little more:
data_df["age_demographic"] = np.where([x >= 25 and x <= 35 for x in data_df["age"]], "yes", "no")

# Make it a categorical variable:
data_df["age_demographic"] = data_df["age_demographic"].astype('category')

data_df.dtypes


# It appears so!

data_df.boxplot("sales", by="age_demographic")

# Alternatively (and nicer handling of outliers):
sns.boxplot(x="age_demographic", y="sales", data=data_df)

# OK, looks like we're swamped by outliers. Time for the log-transformed version:

sns.boxplot(x="age_demographic", y="log_sales", data=data_df)

# Nice.

import statsmodels.api as sm

sm.stats.ttest_ind(data_df.loc[data_df["age_demographic"] == "no", "sales"],
                   data_df.loc[data_df["age_demographic"] == "yes", "sales"])

# More compact, but a little more ninja:
sm.stats.ttest_ind(*(x[1] for x in data_df.groupby("age_demographic")["sales"]))

# t-stat, p-value, df:
# (-81.55845523885793, 0.0, 10998.0)


# As expected: highly significant

# Conclusion: advertising campaign was very successful! Keep advertising.
# Are there more granular ways we can maximize sales?

# xtabs(age_demographic ~ factor(marketing_level), data=data_df)
#
# cor.test( ~ account_balance + sales, data=data_df)

##################################################
### 5: Linear Regression
##################################################

# Take our null model as the mean sales value:
data_df["sales"].mean()

import statsmodels.formula.api as smf
mod_null = smf.ols("sales ~ 1", data=data_df).fit()

mod_null.summary()

# Single factor: account balance
mod0 = smf.ols("sales ~ account_balance", data=data_df).fit()

mod0.summary()

sns.regplot(x="account_balance", y="sales", data=data_df)

plt.hist(mod0.resid)

# Check the effect of age demographic on sales
modDemographic = smf.ols("sales ~ age_demographic", data=data_df).fit()
modDemographic.summary()


# Single factor: age
mod1 = smf.ols("sales ~ age", data=data_df).fit()

mod1.summary()

data_df.plot.scatter(x="age", y="sales", color="black")
plt.title("Sales by customer age")

sns.regplot(x="account_balance", y="sales", data=data_df)

plt.hist(mod1.resid)

# Polynomial in age
mod1b = smf.ols("sales ~ age + I(age**2)", data=data_df).fit()

mod1b.summary()

data_df.plot.scatter(x="age", y="sales")
plt.title("Sales by customer age")

plt.hist(mod1b.resid)

# Clues for multilinear regression

import seaborn as sns

sns.pairplot(
        data_df[["log_account_balance", "age",
                 "marketing_level", "log_sales", "age_demographic"]],
        hue='age_demographic')

# Nice.

mod2 = smf.ols("sales ~ age + I(age**2) + age_demographic + marketing_level + account_balance", data=data_df).fit()
mod2.summary()

mod3 = smf.ols("sales ~ age + I(age**2) + marketing_level:age_demographic + account_balance", data=data_df).fit()

mod3.summary()

# Prediction
# Create a DataFrame that spans the range of our desired parameters:
# Let's see what happens if we turn our marketing UP TO ELEVEN!!!!

pred_df = pd.DataFrame({"age": list(np.arange(16, 65, 5))*2*100*11,
                        "age_demographic": ["yes","no"]*10*100*11,
                        "account_balance": list(np.arange(0, 1000, 10))*10*2*11,
                        "marketing_level": list(np.arange(1, 12))*10*2*100} )


# Generate the predicted sales according to the model :
pred_df['pred_sale_amount'] = mod3.predict(pred_df)

# Plot the model
sns.lmplot("marketing_level", 'pred_sale_amount', data=pred_df, hue="age_demographic")

# YES!

# Try removing one or two vairables from mod3:

mod4 = smf.ols("sales ~ age + I(age**2) + marketing_level:age_demographic", data=data_df).fit()

mod5 = smf.ols("sales ~ I(age**2) + marketing_level:age_demographic", data=data_df).fit()

anova(mod5, mod4)

print(*[f"AIC for model {n}: {x.aic}\n" for n, x in enumerate([mod0, mod1, mod2, mod3, mod4, mod5])])

# Model 3 is the bestus!

# Stepwise AIC: look in scikit-learn. Until next time...

###########################################
# End of Fanning_the_Flames_Python.py
###########################################
