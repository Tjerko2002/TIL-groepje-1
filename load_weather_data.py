import os
import pandas as pd
"""This file opens the weather stations location data, as well as the hourly data of the 5 chosen weather stations.
   These are then converted to pandas dataframes, and exported as csvs. 
"""
# Turn to true to overwrite the csv file with updates.
stations_to_csv = True
weather_5_stations_to_csv = True


# Set the paths to the datafiles. 
file_weather_stations = r"data\locations_weatherstations.csv"
file_path_stations = os.path.join(os.getcwd(),file_weather_stations)

file_weather = r"data\weather_2024.csv"
file_path_weather = os.path.join(os.getcwd(),file_weather)


if stations_to_csv:
    df_stations = pd.read_csv(file_path_stations)
    # Because the csv has emty values as spaces, the dropna function later doesn't work. Therefore, here the csv
    # is opened using na_values=["", " "].
    df_weather = pd.read_csv(
        file_path_weather,
        comment="#",
        skipinitialspace=True,
        na_values=["", " "],     
    )

    df_weather.columns = df_weather.columns.str.strip() # Remove leading spaces in column names. 

    # Drop the rows if these stations do not report rain and hourly rain values. 
    df_weather = df_weather.dropna(subset=["R", "RH"])
    valid_stations = set(df_weather["STN"])

    df_stations = df_stations[df_stations["STN"].isin(valid_stations)]

    # Save the valid stations as csv file

    df_stations.to_csv(os.path.join(os.getcwd(),r"data\df_weatherstations_locations.csv"))



if weather_5_stations_to_csv:
    file_weather_5_stations = r"data\weatherdata_2024_5stations.txt"
    file_path_weather_5_stations = os.path.join(os.getcwd(),file_weather_5_stations)

    df_weather_5_stations = pd.read_csv(
        file_path_weather_5_stations,
        comment='#',        # ignore all lines starting with '#'
        skipinitialspace=True,  # ignore extra spaces after commas
        na_values=['', ' '],    # treat empty fields as NaN
    )
    
    file_path = os.path.join(os.getcwd(),r"data\df_weather_2024.csv")
    df_weather_5_stations.to_csv(file_path)


