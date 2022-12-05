import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

load_dotenv()

M_DATA = os.getenv("MADRID_DATA")
M_PY_DATA_PRE = os.getenv("MADRID_DATA_PY_PREFIX")
M_STAT_DATA = os.getenv("STATIONS_DATA")
C_DATA = os.getenv("CITY_TEMP_DATA")

#Deprecated Constants (shouldn't be here in the first place)
# TARGET_STAT = "28079004"
# ValidStations = ["28079008", "28079016", "28079018", "28079024", "28079039"]

#City temp data curated
with open(C_DATA) as data:
    df = pd.read_csv(data, dtype = str)
    df_mad = df[df.City == "Madrid"]
    df_mad = df_mad["2001" <= df_mad["Year"]]
    df_mad = df_mad[df_mad["Year"] <= "2018"]

    df_tms = df_mad[df_mad["AvgTemperature"] != "-99"]
    df_tms = df_tms.drop(columns = "State")

#City O3 data curated
with open("D:\PyMyScripts\GabrielEst\Mybin\GabrielEstRepo\output\df_n.csv") as data:
    df_oms = pd.read_csv(data, dtype = str)

print("Ozone Data")
print(df_oms.info())
print(df_oms.head())

print("-------------")

print("Temperature Data")
print(df_tms.info())
print(df_tms.head())

print(type(df_oms.date.loc[0]))
print(df_oms.date.loc[0])


























# for DATA_SUFF in os.listdir(M_PY_DATA_PRE):
#     datapath = os.path.join(M_PY_DATA_PRE, DATA_SUFF)
#     with open(datapath) as data:
#         df = pd.read_csv(data, dtype = str)
#         df = df[["date", "station", "O_3"]]
#         df = df[df["station"] == TARGET_STAT]

#         if DATA_SUFF == "madrid_2001.csv":
#             df_m = df
#         else:
#             df_m = pd.concat([df_m, df])

#         print("------------")
#         print(DATA_SUFF)
#         print(df.head(n=1))
#         print(df.tail(n=1))
#         print("------------")

# print(df_m.head())
# print(df_m.tail())

# with pd.HDFStore(M_DATA) as data:
#     df_st = data["master"]
#     df_st_id = pd.Series(df_st.id, dtype = str)
#     for id in df_st_id:
#         print(data["/"+id].head(n=1))
#         print(data["/"+id].tail(n=1))

    
# print(df_curr.describe())
# print(df_curr.head())

# for col in df_curr.columns:
#     print(col)

# plt.plot(df_curr.index, df_curr.O_3)

# print(df_curr.tail())

# for id in ValidStations:
#     for DATA_SUFF in os.listdir(M_PY_DATA_PRE):
#         datapath = os.path.join(M_PY_DATA_PRE, DATA_SUFF)
#         with open(datapath) as data:
#             df = pd.read_csv(data, dtype = str)
#             df = df[["date", "station", "O_3"]]
#             df = df[df["station"] == id]

#             if DATA_SUFF == "madrid_2001.csv":
#                 df_m = df
#             else:
#                 df_m = pd.concat([df_m, df])
#     if id == "28079008":
#         df_n = df_m
#     else:
#         df_n = pd.concat([df_n, df_m])