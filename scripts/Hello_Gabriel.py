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
TARGET_STAT = "28079004"

# #City temp data curated
# with open(C_DATA) as data:
#     df = pd.read_csv(data, dtype = str)
#     df_mad = df[df.City == "Madrid"]
#     df_mad_1 = df_mad["2001" <= df_mad["Year"]]
#     df_mad_1_12 = df_mad_1[df_mad_1["Year"] <= "2012"]

#     df_tms = df_mad_1_12[df_mad_1_12["AvgTemperature"] != "-99"]

ValidStations = ["28079008", "28079016", "28079018", "28079024", "28079039"]

for id in ValidStations:
    for DATA_SUFF in os.listdir(M_PY_DATA_PRE):
        datapath = os.path.join(M_PY_DATA_PRE, DATA_SUFF)
        with open(datapath) as data:
            df = pd.read_csv(data, dtype = str)
            df = df[["date", "station", "O_3"]]
            df = df[df["station"] == id]

            if DATA_SUFF == "madrid_2001.csv":
                df_m = df
            else:
                df_m = pd.concat([df_m, df])
    if id == "28079008":
        df_n = df_m
    else:
        df_n = pd.concat([df_n, df_m])

df_n.to_csv(r"D:\PyMyScripts\GabrielEst\Mybin\GabrielEstRepo\output\df_n.csv")

print(df_n.O_3.astype(float).describe())
print(df_n.head())
print(df_n.tail())

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