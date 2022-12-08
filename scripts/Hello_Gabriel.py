import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pymannkendall as mk
import math
from sklearn.linear_model import LinearRegression
from scipy import stats

#Load .env
load_dotenv()

#Get .env variables

#Deprecated, used to create the intermediate csv for the O3 data
# M_DATA = os.getenv("MADRID_DATA")
# M_PY_DATA_PRE = os.getenv("MADRID_DATA_PY_PREFIX")
# M_STAT_DATA = os.getenv("STATIONS_DATA")

C_DATA = os.getenv("CITY_TEMP_DATA")
INTER_O3_DATA = os.getenv("INTERMEDIATE_O3_DATA")

#------------------------------------

#Open city temp data
with open(C_DATA) as data:
    df = pd.read_csv(data, dtype = str)

#Get the entries of Madrid from years 2001 to 2018 and drop NaN flags ("-99"), also, drop "State" column,
#it's irrelevant and Null outside of US.
df_mad = df[df.City == "Madrid"]
df_mad = df_mad["2001" <= df_mad["Year"]]
df_mad = df_mad[df_mad["Year"] <= "2018"]
df_mad = df_mad[df_mad["AvgTemperature"] != "-99"]
df_tms = df_mad.drop(columns = "State")

#Create datetime column and reset index
df_tms = df_tms.assign(date = df_tms["Year"] + "-" + df_tms["Month"] + "-" + df_tms["Day"])
df_tms["date"] = pd.to_datetime(df_tms["date"], format = r"%Y-%m-%d")
df_tms = df_tms.sort_values("date").reset_index()

#Drop irrelevant columns, reorganize them and truncate them to the desired date
df_tms = df_tms.drop(columns = ["index", "Region", "Country", "City", "Month", "Day", "Year"])
df_tms = df_tms.reindex(columns = ["date", "AvgTemperature"])
df_tms = df_tms[df_tms["date"] <= datetime(2018,5,1)]

#Average the measurings in the same date, drop NaN values and reset index,
#df_tmss is the desired dataframe for the temperature data
df_tms = df_tms.groupby("date", as_index = False, dropna = True).mean()
df_tmss = df_tms.reset_index().drop(columns = "index")

#Average the measurings in the same month, standarize days , df_tmssg is used for the seasonal test.
df_tmssg = df_tmss.groupby(pd.Grouper(key = "date", freq = "M")).mean().reset_index()
df_tmssg["date"] = df_tmssg["date"].apply(lambda x: datetime(year = x.year, month = x.month, day = 1))

#------------------------------------

#Open city O3 data (This data was previously curated from several csv's)
with open(INTER_O3_DATA) as data:
    df_oms = pd.read_csv(data, dtype = str)

#Create a datetime column, sort values by datetime and reset index
df_oms["date"] = df_oms["date"].apply(lambda x: x[:10])
df_oms["date"] = pd.to_datetime(df_oms["date"], format = r"%Y-%m-%d")
df_oms = df_oms.sort_values("date").reset_index()

#Drop irrelevant columns and transform O3 column to float (was str)
df_oms = df_oms.drop(columns = ["index", "Unnamed: 0", "station"])
df_oms["O_3"] = df_oms["O_3"].astype(float)

#Average the measurings in the same day, drop NaN values and reset index,
#df_omss is the desired dataframe for ozone data
df_oms = df_oms.groupby("date", as_index = False, dropna = True).mean()
df_omss = df_oms.reset_index().drop(columns = "index")

#Average the measurings in the same month, standarize days, df_omssg is used for the seasonal test.
df_omssg = df_omss.groupby(pd.Grouper(key = "date", freq = "M")).mean().reset_index()
df_omssg["date"] = df_omssg["date"].apply(lambda x: datetime(year = x.year, month = x.month, day = 1))

#------------------------------------
#Working with standarized data for linear regression

#Standarized data
df_tmstd = df_tmssg.assign(std_temp = (df_tmssg["AvgTemperature"]-df_tmssg["AvgTemperature"].mean())/df_tmssg["AvgTemperature"].std())
df_omstd = df_omssg.assign(std_O_3 = (df_omssg["O_3"]-df_omssg["O_3"].mean())/df_omssg["O_3"].std())

#Calculate mean of months by year
df_tmstdg = df_tmstd.groupby(pd.Grouper(key = "date", freq = "Y")).mean().reset_index()
df_omstdg = df_omstd.groupby(pd.Grouper(key = "date", freq = "Y")).mean().reset_index()

#Create column with each month divided by the year mean, say, the weighted column
df_tmstdg12 = pd.DataFrame(np.repeat(df_tmstdg.values, 12, axis = 0))
df_tmstdg12.columns = df_tmstdg.columns
df_tmstd = df_tmstd.assign(year_mean = df_tmstdg12["std_temp"])
df_tmstd = df_tmstd.assign(w_std_temp = df_tmstd["std_temp"]/df_tmstd["year_mean"])

df_omstdg12 = pd.DataFrame(np.repeat(df_omstdg.values, 12, axis = 0))
df_omstdg12.columns = df_omstdg.columns
df_omstd = df_omstd.assign(year_mean = df_omstdg12["std_O_3"])
df_omstd = df_omstd.assign(w_std_O_3 = df_omstd["std_O_3"]/df_omstd["year_mean"])

#Calculate mean by month of the weighted column, named coef
df_tmstd = df_tmstd.assign(month = df_tmstd["date"].apply(lambda x: x.month))
df_tmstd_coef = df_tmstd.drop(columns = ["date", "AvgTemperature", "std_temp", "year_mean"]).groupby("month").mean()

df_omstd = df_omstd.assign(month = df_omstd["date"].apply(lambda x: x.month))
df_omstd_coef = df_omstd.drop(columns = ["date", "O_3", "std_O_3", "year_mean"]).groupby("month").mean()

#Divide each data by coef, named destationalized data, dd
df_tmstd = df_tmstd.join(df_tmstd_coef, on = "month", validate = "m:1", lsuffix = "_a", rsuffix = "_mbm")
df_tmstd = df_tmstd.assign(dd = df_tmstd["std_temp"]/df_tmstd["w_std_temp_mbm"])

df_omstd = df_omstd.join(df_omstd_coef, on = "month", validate = "m:1", lsuffix = "_a", rsuffix = "_mbm")
df_omstd = df_omstd.assign(dd = df_omstd["std_O_3"]/df_omstd["w_std_O_3_mbm"])






#DESTATIONALIZATION NO NORMALIZED

# df_tmstd = df_tmssg.assign(std_temp = (df_tmssg["AvgTemperature"]-df_tmssg["AvgTemperature"].mean())/df_tmssg["AvgTemperature"].std())
# df_omstd = df_omssg.assign(std_O_3 = (df_omssg["O_3"]-df_omssg["O_3"].mean())/df_omssg["O_3"].std())

# #Calculate mean of months by year
# df_tmstdg = df_tmstd.groupby(pd.Grouper(key = "date", freq = "Y")).mean().reset_index()
# df_omstdg = df_omstd.groupby(pd.Grouper(key = "date", freq = "Y")).mean().reset_index()

# #Create column with each month divided by the year mean, say, the weighted column
# df_tmstdg12 = pd.DataFrame(np.repeat(df_tmstdg.values, 12, axis = 0))
# df_tmstdg12.columns = df_tmstdg.columns
# df_tmstd = df_tmstd.assign(year_mean = df_tmstdg12["AvgTemperature"])
# df_tmstd = df_tmstd.assign(w_std_temp = df_tmstd["AvgTemperature"]/df_tmstd["year_mean"])

# df_omstdg12 = pd.DataFrame(np.repeat(df_omstdg.values, 12, axis = 0))
# df_omstdg12.columns = df_omstdg.columns
# df_omstd = df_omstd.assign(year_mean = df_omstdg12["O_3"])
# df_omstd = df_omstd.assign(w_std_O_3 = df_omstd["O_3"]/df_omstd["year_mean"])

# #Calculate mean by month of the weighted column, named coef
# df_tmstd = df_tmstd.assign(month = df_tmstd["date"].apply(lambda x: x.month))
# df_tmstd_coef = df_tmstd.drop(columns = ["date", "AvgTemperature", "std_temp", "year_mean"]).groupby("month").mean()

# df_omstd = df_omstd.assign(month = df_omstd["date"].apply(lambda x: x.month))
# df_omstd_coef = df_omstd.drop(columns = ["date", "O_3", "std_O_3", "year_mean"]).groupby("month").mean()

# #Divide each data by coef, named destationalized data, dd
# df_tmstd = df_tmstd.join(df_tmstd_coef, on = "month", validate = "m:1", lsuffix = "_a", rsuffix = "_mbm")
# df_tmstd = df_tmstd.assign(dd = df_tmstd["AvgTemperature"]/df_tmstd["w_std_temp_mbm"])

# df_omstd = df_omstd.join(df_omstd_coef, on = "month", validate = "m:1", lsuffix = "_a", rsuffix = "_mbm")
# df_omstd = df_omstd.assign(dd = df_omstd["O_3"]/df_omstd["w_std_O_3_mbm"])







#------------------------------------ END OF CLEANING

# We use the Mann-Kendall test for seasonal time-series data
# Hirsch, R.M., Slack, J.R. and Smith, R.A. (1982) proposed this test to calculate the seasonal trend.
# Docs on the MannKedall package can be found in https://pypi.org/project/pymannkendall/
print(mk.seasonal_test(df_tmssg["AvgTemperature"], period = 12), "\n")
print("---------------------", "\n")
print(mk.seasonal_test(df_omssg["O_3"], period = 12))

#Test
print(mk.seasonal_test(df_tmstd["std_temp"], period = 12))
print(mk.seasonal_test(df_omstd["std_O_3"], period = 12))







#------------------------------------ END OF ANALYSIS

#Transform date to ordinal
df_tmstd = df_tmstd.assign(o_date = df_tmstd["date"].map(datetime.toordinal))
df_omstd = df_omstd.assign(o_date = df_omstd["date"].map(datetime.toordinal))

#Test
print(df_tmstd.tail())

#Drop outliers
df_tmstd = df_tmstd[np.abs(stats.zscore(df_tmstd["dd"])) < 2].reset_index().drop(columns = "index")
df_omstd = df_omstd[np.abs(stats.zscore(df_omstd["dd"])) < 2].reset_index().drop(columns = "index")

#Test
print(df_tmstd.tail())

#Perform regression
X_t = df_tmstd.reset_index()["index"].values.reshape(-1, 1)
Y_t = df_tmstd["dd"].values.reshape(-1, 1)
linear_regressor_t = LinearRegression().fit(X_t, Y_t)
Y_t_pred = linear_regressor_t.predict(X_t)

X_o = df_omstd.reset_index()["index"].values.reshape(-1, 1)
Y_o = df_omstd["dd"].values.reshape(-1, 1)
linear_regressor_o = LinearRegression().fit(X_o, Y_o)
Y_o_pred = linear_regressor_o.predict(X_o)






#------------------------------------ END OF LINEAR REGRESSION

#Plotting of temperature and ozone levels across time
df_tmss.plot(x = "date", y = "AvgTemperature")
df_omss.plot(x = "date", y = "O_3")
df_tmssg.plot(x = "date", y = "AvgTemperature")
df_omssg.plot(x = "date", y = "O_3")

df_plot = pd.DataFrame(data = {"X_t": list(map(lambda x: x[0], X_t)), "Y_t": list(map(lambda x: x[0], Y_t))})
df_plot.plot(x = "X_t", y = "Y_t", kind = "scatter")
plt.plot(X_t, Y_t_pred, color = "red")

print("Temp coef: ", "{:.8f}".format(float(linear_regressor_t.coef_)))
print("Temp int: ", "{:.8f}".format(float(linear_regressor_t.intercept_)))
print("O3 coef: ", "{:.8f}".format(float(linear_regressor_o.coef_)))
print("O3 int: ", "{:.8f}".format(float(linear_regressor_o.intercept_)))
print(df_tmstd[df_tmstd["month"] == 1].head(n = 18))

# df_plot = pd.DataFrame(data = {"X_o": list(map(lambda x: x[0], X_o)), "Y_o": list(map(lambda x: x[0], Y_o))})
# df_plot.plot(x = "X_o", y = "Y_o", kind = "scatter")
# plt.plot(X_o, Y_o_pred, color = "red")
plt.show()

#------------------------------------ TESTS

#Linear regression of the dd

# print(df_tmstd.head())
# print(df_omstd.head())
# print(df_tmstdg.head())
# print(df_omstdg.head())
# print(df_tmstd_coef.head())