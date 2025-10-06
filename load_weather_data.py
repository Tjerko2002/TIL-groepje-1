import os
import pandas as pd
"""This file opens and cleans the datasets for the weather data of KNMI. It stores the data as pandas dataframe in pickle format."""

file_weather_stations = "data\locations_weatherstations.csv"
file_path = os.path.join(os.getcwd(),file_weather_stations)
print(str(file_path))