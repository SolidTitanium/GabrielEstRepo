import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pymannkendall as mk

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
df_tms = df_tms.groupby("date", as_index = False).mean().dropna()
df_tmss = df_tms.reset_index().drop(columns = "index")

#Average the measurings in the same month, df_tmssg is used for the seasonal test.
df_tmssg = df_tmss.groupby(pd.Grouper(key = "date", freq = "M"), as_index = False).mean()

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
df_oms = df_oms.groupby("date", as_index = False).mean().dropna()
df_omss = df_oms.reset_index().drop(columns = "index")

#Average the measurings in the same month, df_omssg is used for the seasonal test.
df_omssg = df_omss.groupby(pd.Grouper(key = "date", freq = "M"), as_index = False).mean()

#------------------------------------ END OF CLEANING

#We use the Mann-Kendall test for seasonal time-series data
#Hirsch, R.M., Slack, J.R. and Smith, R.A. (1982) proposed this test to calculate the seasonal trend.
#Docs on the MannKedall package can be found in https://pypi.org/project/pymannkendall/
print(mk.seasonal_test(df_tmssg["AvgTemperature"], period = 12), "\n")
print("---------------------", "\n")
print(mk.seasonal_test(df_omssg["O_3"], period = 12))

#------------------------------------ END OF ANALYSIS

#Plotting of temperature and ozone levels across time
df_tmss.plot(x = "date", y = "AvgTemperature")
df_omss.plot(x = "date", y = "O_3")
plt.show()