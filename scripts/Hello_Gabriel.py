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

with open(M_STAT_DATA) as data:
    df = pd.read_csv(data, dtype = str)
    stat_ids = tuple(_ for _ in df.id)

ValidStations = list(map(lambda x: int(x), stat_ids))
print(repr(ValidStations))
InvalidStation = []

for id in stat_ids:
    for DATA_SUFF in os.listdir(M_PY_DATA_PRE):
        datapath = os.path.join(M_PY_DATA_PRE, DATA_SUFF)
        with open(datapath) as data:
            df = pd.read_csv(data, dtype = str)
            df = df[["date", "station", "O_3"]]
            df = df[df["station"] == id]
            if df["O_3"].any() == False:
                ValidStations.pop(ValidStations.index(int(id)))
                InvalidStation.append(int(id))
                break

            # if DATA_SUFF == "madrid_2001.csv":
            #     df_m = df
            # else:
            #     df_m = pd.concat([df_m, df])

print("VALID: ", ValidStations)
print("INVALID: ", InvalidStation)

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