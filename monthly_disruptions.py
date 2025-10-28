"""This file produces a bar chart of the number of disruptions per month, together with a line that shows the temperature per month throughout the year """

import pandas as pd
import matplotlib.pyplot as plt

# read file with train disruptions within circle
df_circle_disruptions = pd.read_parquet("data/disruptions_withincircle.parquet")

# Test if the file is read properly 
print(df_circle_disruptions.head())

# Convert start_time to a datetime which can be used in Pandas to only look at each month later on
df_circle_disruptions["start_time"] = pd.to_datetime(df_circle_disruptions["start_time"])

# The datetime is now filtered based on the month ("M"), it groups and calculates the number of rows for each month.
monthly = (
    df_circle_disruptions.groupby(df_circle_disruptions["start_time"].dt.to_period("M"))
    .size()                                            # Counts number of rows per month
    .reset_index(name="disruption_number")             # Creates a new dataframe with the total number of disruptions
    .rename(columns={"start_time": "month_period"})    # Changes the column name to month
)

# Test if the file gives the wanted output
print(monthly)

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