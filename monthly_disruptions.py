"""This file produces a bar chart of the number of disruptions per month, together with a line that shows the weather data per month throughout the year """

import pandas as pd
import matplotlib.pyplot as plt
import os
# pd.set_option("display.max_rows", None)      # show all rows
# pd.set_option("display.max_columns", None)   # show all columns
# pd.set_option("display.width", 0)            # no line wrapping

# read file with train disruptions within circle
df_circle_disruptions = pd.read_parquet("data/disruptions_withincircle.parquet")

# Only select the causes that could be related to weather
causes_to_keep = [
    "An object in the overhead wires",
    "broken down train",
    "damaged railway bridge",
    "defective point",
    "defective railway track",
    "hindrance on the railway",
    "level crossing failure",
    "signal failure"
]

# Filter the dataframe
df_filtered_circle_disruptions = df_circle_disruptions[df_circle_disruptions["cause_en"].isin(causes_to_keep)]

# Test if the file is read properly
#print(df_filtered_circle_disruptions['cause_en'])

# Convert start_time to a datetime which can be used in Pandas to only look at each month later on
df_filtered_circle_disruptions["start_time"] = pd.to_datetime(df_filtered_circle_disruptions["start_time"])

# The datetime is now filtered based on the month ("M"), it groups and calculates the number of rows for each month.
monthly = (
    df_filtered_circle_disruptions.groupby(df_filtered_circle_disruptions["start_time"].dt.to_period("M"))
    .size()                                            # Counts number of rows per month
    .reset_index(name="disruption_number")             # Creates a new dataframe with the total number of disruptions
    .rename(columns={"start_time": "month_period"})    # Changes the column name to month_period
)

# Test if the file gives the wanted output
#print(monthly)

# Convert the datetime which consists of periods back to timestamps to be able to plot later on.
monthly["month"] = monthly["month_period"].dt.to_timestamp()

# Plot a bar chart with the total number of disruptions per month.
plt.figure(figsize=(10,6))
plt.bar(monthly["month"].dt.strftime("%b"), monthly["disruption_number"])
plt.title("Train Disruptions per Month (2024)")
plt.xlabel("Month")
plt.ylabel("Number of Disruptions")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()


####################################################


## This new code provides the bar chart for the total number of disruption minutes per month

import pandas as pd
import matplotlib.pyplot as plt

# read file with train disruptions within circle
df_circle_disruptions = pd.read_parquet("data/disruptions_withincircle.parquet")

# Only select the causes that could be related to weather
causes_to_keep = [
    "An object in the overhead wires",
    "broken down train",
    "damaged railway bridge",
    "defective point",
    "defective railway track",
    "hindrance on the railway",
    "level crossing failure",
    "signal failure"
]

# Filter the dataframe
df_filtered_circle_disruptions = df_circle_disruptions[df_circle_disruptions["cause_en"].isin(causes_to_keep)]

# Test if the file is read properly 
#print(df_filtered_circle_disruptions['cause_en'])

# Convert start_time to a datetime which can be used in Pandas to only look at each month later on
df_filtered_circle_disruptions["start_time"] = pd.to_datetime(df_filtered_circle_disruptions["start_time"])

# The datetime is now filtered based on the month ("M"), it groups and calculates the number of rows for each month.
monthly = (
    df_filtered_circle_disruptions.groupby(df_filtered_circle_disruptions["start_time"].dt.to_period("M"))
    ["duration_minutes"].sum()                         # Sums the total minutes per month
    .reset_index(name="disruption_minutes")            # Creates a new dataframe with the total number of disruption minutes
    .rename(columns={"start_time": "month_period"})    # Changes the column name to month_period
)

# Test if the file gives the wanted output
# print(monthly)

# Convert the datetime which consists of periods back to timestamps to be able to plot later on.
monthly["month"] = monthly["month_period"].dt.to_timestamp()

# Plot a bar chart with the total number of disruption minutes per month.
plt.figure(figsize=(10,6))
plt.bar(monthly["month"].dt.strftime("%b"), monthly["disruption_minutes"])
plt.title("Train Disruptions Minutes per Month (2024)")
plt.xlabel("Month")
plt.ylabel("Disruption Minutes")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()


# To dos for plotten weerdata:
# Kijken hoeveel procent van de treinen rijden tussen 8:00 en 22:00 bijvoorbeeld. Stel dit is 90%, dan neem je weerdata tussen 8:00 en 22:00 keer 0.9
# Bepaal gemiddelde voor elke maand met deze weighted factors

# # Now, the weather data can be used to implement in the existing plot
# file_path = os.path.join(os.getcwd(),r"data\df_weather_5_stations.parquet")
# weather_data = pd.read_parquet(file_path)
# print(weather_data)

# df_weather_mean = (
#     weather_data.groupby("timestamp")[["T", "FH", "FX", "RH", "P", "N", "R", "S"]]
#     .mean()
#     .reset_index()
# )
