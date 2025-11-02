"""This file produces bar charts of the number of disruptions per month, together with a line that shows the corresponding weather data per month throughout the year """

import pandas as pd
import matplotlib.pyplot as plt
import os

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

# For monthly disruptions
# The datetime is now filtered based on the month ("M"), it groups and calculates the number of rows for each month.
monthly_count = (
    df_filtered_circle_disruptions.groupby(df_filtered_circle_disruptions["start_time"].dt.to_period("M"))
    .size()                                            # Counts number of rows per month
    .reset_index(name="disruption_number")             # Creates a new dataframe with the total number of disruptions
    .rename(columns={"start_time": "month_period"})    # Changes the column name to month_period
)

# Test if the file gives the wanted output
#print(monthly_count)

# Convert the datetime which consists of periods back to timestamps to be able to plot later on.
monthly_count["month"] = monthly_count["month_period"].dt.to_timestamp()


# For monthly disruption minutes
# The datetime is now filtered based on the month ("M"), it groups and calculates the number of rows for each month.
monthly_minutes = (
    df_filtered_circle_disruptions.groupby(df_filtered_circle_disruptions["start_time"].dt.to_period("M"))
    ["duration_minutes"].sum()                         # Sums the total minutes per month
    .reset_index(name="disruption_minutes")            # Creates a new dataframe with the total number of disruption minutes
    .rename(columns={"start_time": "month_period"})    # Changes the column name to month_period
)

# Test if the file gives the wanted output
# print(monthly_minutes)

# Convert the datetime which consists of periods back to timestamps to be able to plot later on.
monthly_minutes["month"] = monthly_minutes["month_period"].dt.to_timestamp()



######## Now, the weather data can be used to implement it in the final plot as well

# The data file of the weather data from the five stations is read and checked
file_path = os.path.join(os.getcwd(),r"data\df_weather_5_stations.parquet")
weather_data = pd.read_parquet(file_path)
print(weather_data)

# HH = 24 is changed to HH = 0 for the next day, because 24 at the end is not a valid datetime string and therefore produces a ValueError if not altered. 
mask = weather_data["HH"] == 24
if mask.any():
    weather_data.loc[mask, "HH"] = 0
    weather_data.loc[mask, "YYYYMMDD"] = (
        pd.to_datetime(weather_data.loc[mask, "YYYYMMDD"].astype(str), format="%Y%m%d")
        + pd.Timedelta(days=1)
    ).dt.strftime("%Y%m%d").astype(int)

# The columns in the data file related to the date and the hour are rewritten as one string for data grouping and further analysis later on
weather_data["datetime"] = pd.to_datetime(
    weather_data["YYYYMMDD"].astype(str) + weather_data["HH"].astype(str).str.zfill(2),
    format="%Y%m%d%H"
)

# Weather data is averaged for each datetime, defined above, over all five stations
temp_rain = weather_data.groupby("datetime")[["T", "RH"]].mean().reset_index()
print(temp_rain)

# Function is used that returns the weighted temperature and rain values based on what hour each value is measured.
# This comes from the fact that in between 6:00 and 24:00 (daytime), 92.20% of the trains are active.
# Therefore, the temperature and rain values within this range account for 92.20% of the average.
def hour_weight(hour):
    if 6 <= hour < 24:
        return 0.9220 / 18  # 18 hours of "daytime" (06:00 - 24:00)
    else:
        return (1 - 0.9220) / 6  # 6 hours of "nighttime" (24:00 - 06:00)

temp_rain["hour"] = temp_rain["datetime"].dt.hour
temp_rain["weight"] = temp_rain["hour"].apply(hour_weight)

# Weighted temperature calculation
temp_rain["weighted_temp"] = temp_rain["T"] * temp_rain["weight"]

# Weighted rain calculation
temp_rain["weighted_precip"] = temp_rain["RH"] * temp_rain["weight"]

# The weighted temperature average and total weighted rain are calculated for each individual month. 
# This is done by dividing the total sum of the weighted temperatures in a month by the total weighted average sum.
# The weighted total rain per hour is summed for each month to get the total montly value.
monthly_temp_rain = (
    temp_rain.groupby(temp_rain["datetime"].dt.to_period("M"))
    .apply(lambda g: pd.Series({
        "avg_weighted_temp": g["weighted_temp"].sum() / g["weight"].sum(),
        "total_weighted_precip": g["weighted_precip"].sum()
    }))
    .reset_index()
)

# Convert the datetime which consists of periods back to timestamps to be able to plot later on.
monthly_temp_rain["month"] = monthly_temp_rain["datetime"].dt.to_timestamp()

# Merge both datasets of disruption and temperature/rain together to make the plot. It looks for the columns "month" in both datasets which are then combined.
# 'inner' ensures only months will be kept that both have disruption and weather data. 
monthly_count_combined = pd.merge(monthly_count, monthly_temp_rain, on="month", how="inner")
monthly_minutes_combined = pd.merge(monthly_minutes, monthly_temp_rain, on="month", how="inner")

# For investigating wind effects, the average wind speed (FH) is compared to a wind speed threshold which indicates stormy winds.
wind_threshold = 100 # in 0.1 m/s

# Average FH over all five stations for each datetime
avg_wind = weather_data.groupby("datetime")[["FH"]].mean().reset_index()

# Add a new column for hours where FH > threshold
avg_wind["high_wind"] = avg_wind["FH"] > wind_threshold

# Calculate the frequency where the average windspeed FH > threshold per month by taking the sum of all occasions
monthly_high_wind = (
    avg_wind.groupby(avg_wind["datetime"].dt.to_period("M"))
    ["high_wind"]
    .sum()
    .reset_index(name="hours_high_wind")
)

# Convert the datetime which consists of periods back to timestamps to be able to plot later on.
monthly_high_wind["month"] = monthly_high_wind["datetime"].dt.to_timestamp()

# Merge both datasets of disruption and windspeed frequency together to make the plot. It looks for the columns "month" in both datasets which are then combined.
# 'inner' ensures only months will be kept that both have disruption and weather data.
monthly_count_wind = pd.merge(monthly_count, monthly_high_wind, on="month", how="inner")
monthly_minutes_wind = pd.merge(monthly_minutes, monthly_high_wind, on="month", how="inner")




# Plot of the disruptions per month, together with the average weighted temperature in each month. 
fig1, ax1 = plt.subplots(figsize=(10,6))

# Bar chart: number of disruptions (first axis)
ax1.bar(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["disruption_number"], label="Number of Disruptions", alpha=0.7)
ax1.set_xlabel("Month")
ax1.set_ylabel("Number of Disruptions")
ax1.grid(axis="y", linestyle="--", alpha=0.7)

# Line: temperature (second axis)
ax2 = ax1.twinx()
ax2.plot(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["avg_weighted_temp"] / 10, color="red", marker="o", label="Avg Temp (°C)")
ax2.set_ylabel("Average Temperature (°C)")

# Title and layout
plt.title("Train Disruptions And Weighted Average Temperature Per Month (2024)")
fig1.tight_layout()

# Add legends for both axes
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")



# Plot of the disruption minutes per month, together with the average weighted temperature in each month. 
fig2, ax3 = plt.subplots(figsize=(10,6))

# Bar chart: disruption minutes (first axis)
ax3.bar(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["disruption_minutes"], label="Disruption Minutes", alpha=0.7)
ax3.set_xlabel("Month")
ax3.set_ylabel("Disruption Minutes")
ax3.grid(axis="y", linestyle="--", alpha=0.7)

# Line: temperature (second axis)
ax4 = ax3.twinx()
ax4.plot(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["avg_weighted_temp"] / 10, color="red", marker="o", label="Avg Temp (°C)")
ax4.set_ylabel("Average Temperature (°C)")

# Title and layout
plt.title("Train Disruption Minutes And Weighted Average Temperature Per Month (2024)")
fig2.tight_layout()

# Add legends for both axes
ax3.legend(loc="upper left")
ax4.legend(loc="upper right")



# Plot of the disruptions per month, together with the total weighted rainfall in each month.
fig3, ax5 = plt.subplots(figsize=(10,6))

# Bar chart: number of disruptions (first axis)
ax5.bar(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["disruption_number"], label="Number of Disruptions", alpha=0.7)
ax5.set_xlabel("Month")
ax5.set_ylabel("Number of Disruptions")
ax5.grid(axis="y", linestyle="--", alpha=0.7)

# Line: rainfall (second axis)
ax6 = ax5.twinx()
ax6.plot(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["total_weighted_precip"], color="blue", marker="s", label="Total Rainfall (mm)")
ax6.set_ylabel("Total Rainfall (mm)")

# Title and layout
plt.title("Train Disruptions And Total Weighted Rainfall Per Month (2024)")
fig3.tight_layout()

# Add legends for both axes
ax5.legend(loc="upper left")
ax6.legend(loc="upper right")


# Plot of the disruption minutes per month, together with the total weighted rainfall in each month.
fig4, ax7 = plt.subplots(figsize=(10,6))

# Bar chart: disruption minutes (first axis)
ax7.bar(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["disruption_minutes"], label="Disruption Minutes", alpha=0.7)
ax7.set_xlabel("Month")
ax7.set_ylabel("Disruption Minutes")
ax7.grid(axis="y", linestyle="--", alpha=0.7)

# Line: rainfall (second axis)
ax8 = ax7.twinx()
ax8.plot(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["total_weighted_precip"], color="blue", marker="s", label="Total Rainfall (mm)")
ax8.set_ylabel("Total Rainfall (mm)")

# Title and layout
plt.title("Train Disruption Minutes And Total Weighted Rainfall Per Month (2024)")
fig4.tight_layout()

# Add legends for both axes
ax7.legend(loc="upper left")
ax8.legend(loc="upper right")


# Plot of the disruption per month, together with the hourly windspeed frequency above the threshold in each month.
fig6, ax11 = plt.subplots(figsize=(10,6))

# Bar chart: number of disruptions (first axis)
ax11.bar(monthly_count_wind["month"].dt.strftime("%b"), monthly_count_wind["disruption_number"],
         label="Number of Disruptions", alpha=0.7)
ax11.set_xlabel("Month")
ax11.set_ylabel("Number of Disruptions")
ax11.grid(axis="y", linestyle="--", alpha=0.7)

# Line: frequency of strong wind hours (second axis)
ax12 = ax11.twinx()
ax12.plot(monthly_count_wind["month"].dt.strftime("%b"), monthly_count_wind["hours_high_wind"],
          color="green", marker="^", label=f"Hours with FH > {wind_threshold/10*3.6:.0f} km/h")
ax12.set_ylabel(f"Hours with FH > {wind_threshold/10*3.6:.0f} km/h")

# Title and layout
plt.title(f"Train Disruptions And Frequency of Mean Winds (> {wind_threshold/10*3.6:.0f} km/h) Per Month (2024)")

fig6.tight_layout()

# Add legends for both axes
ax11.legend(loc="upper left")
ax12.legend(loc="upper right")

# Plot of the disruption minutes per month, together with the hourly windspeed frequency above the threshold in each month.
fig5, ax9 = plt.subplots(figsize=(10,6))

# Bar chart: disruption minutes (first axis)
ax9.bar(monthly_minutes_wind["month"].dt.strftime("%b"), monthly_minutes_wind["disruption_minutes"],
        label="Disruption Minutes", alpha=0.7)
ax9.set_xlabel("Month")
ax9.set_ylabel("Disruption Minutes")
ax9.grid(axis="y", linestyle="--", alpha=0.7)

# Line: frequency of strong wind hours (second axis)
ax10 = ax9.twinx()
ax10.plot(monthly_minutes_wind["month"].dt.strftime("%b"), monthly_minutes_wind["hours_high_wind"],
          color="green", marker="^", label=f"Hours with FH > {wind_threshold/10*3.6:.0f} km/h")
ax10.set_ylabel(f"Hours with FH > {wind_threshold/10*3.6:.0f} km/h")

# Title and layout
plt.title(f"Train Disruptions And Frequency of Mean Winds (> {wind_threshold/10*3.6:.0f} km/h) Per Month (2024)")

fig5.tight_layout()

# Add legends for both axes
ax9.legend(loc="upper left")
ax10.legend(loc="upper right")

plt.show()
