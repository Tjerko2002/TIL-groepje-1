import os
import pandas as pd
"""This file opens and cleans the datasets for the weather data of KNMI. It stores the data as pandas dataframe in pickle format."""

filename = "weather_2024.txt"
file_path = os.path.join(os.getcwd(),filename)
print(str(file_path))