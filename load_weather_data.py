import os
import pandas as pd
"""This file opens and cleans the datasets for the weather data of KNMI. It stores the data as pandas dataframe in pickle format."""

file_weather_stations = r"data\locations_weatherstations.csv"
file_path_stations = os.path.join(os.getcwd(),file_weather_stations)

file_weather = r"data\weather_2024.csv"
file_path_weather = os.path.join(os.getcwd(),file_weather)


df_stations = pd.read_csv(file_path_stations)
# Because the csv has emty values as spaces, the dropna function later doesn't work. Therefore, here the csv
# is opened using na_values=["", " "].
df_weather = pd.read_csv(
    file_path_weather,
    comment="#",
    skipinitialspace=True,
    na_values=["", " "],     
)

df_weather.columns = df_weather.columns.str.strip() # The dataset has leading spaces in column names. 

# Drop the rows if these stations do not report rain and hourly rain values. 
df_weather = df_weather.dropna(subset=["R", "RH"])
valid_stations = set(df_weather["STN"])

df_stations = df_stations[df_stations["STN"].isin(valid_stations)]

for station in df_stations["NAME"]:
    print(station)