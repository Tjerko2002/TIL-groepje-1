import pandas as pd
import matplotlib.pyplot as plt
import os
"""This file produces bar charts of the number of disruptions per month, together with a line that shows the corresponding weather data per month throughout the year """

# read file with potential weather related train disruptions within circle
df_circle_disruptions = pd.read_csv("data/disruptions_filtered_selected_causes.csv")

# Convert start_time to a datetime which can be used in Pandas to only look at each month later on
df_circle_disruptions["start_time"] = pd.to_datetime(df_circle_disruptions["start_time"])

# For monthly disruptions
# The datetime is now filtered based on the month ("M"), it groups and calculates the number of rows for each month.
monthly_count = (
    df_circle_disruptions.groupby(df_circle_disruptions["start_time"].dt.to_period("M"))
    .size()                                            # Counts number of rows per month
    .reset_index(name="disruption_number")             # Creates a new dataframe with the total number of disruptions
    .rename(columns={"start_time": "month_period"})    # Changes the column name to month_period
)

# Convert the datetime which consists of periods back to timestamps to be able to plot later on.
monthly_count["month"] = monthly_count["month_period"].dt.to_timestamp()


# For monthly disruption minutes
# The datetime is now filtered based on the month ("M"), it groups and calculates the number of rows for each month.
monthly_minutes = (
    df_circle_disruptions.groupby(df_circle_disruptions["start_time"].dt.to_period("M"))
    ["duration_minutes"].sum()                         # Sums the total minutes per month
    .reset_index(name="disruption_minutes")            # Creates a new dataframe with the total number of disruption minutes
    .rename(columns={"start_time": "month_period"})    # Changes the column name to month_period
)

# Convert the datetime which consists of periods back to timestamps to be able to plot later on.
monthly_minutes["month"] = monthly_minutes["month_period"].dt.to_timestamp()



# Now, the weather data can be used to implement it in the final plot as well

# The data file of the weather data from the five stations is read and checked
file_path = os.path.join(os.getcwd(),r"data\df_weather_2024.csv")
weather_data = pd.read_csv(file_path)

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

# Weather data for temperature, rain fall and windspeed is averaged for each datetime, defined above, over all five stations
temp_rain_wind = weather_data.groupby("datetime")[["T", "RH", "FH"]].mean().reset_index()
# print(temp_rain)

# Convert 0.1 mm as stated in the dataset to mm
temp_rain_wind["RH"] = temp_rain_wind["RH"] / 10 

# Convert 0.1 (°C) as stated in the dataset to (°C)
temp_rain_wind["T"] = temp_rain_wind["T"] / 10 

# Convert 0.1 (m/s) as stated in the dataset to (m/s)
temp_rain_wind["FH"] = temp_rain_wind["FH"] / 10 

# Function is used that returns the weighted temperature based on what hour each value is measured.
# This comes from the fact that in between 6:00 and 24:00 (daytime), 92.20% of the trains are active.
# Therefore, the temperature within this range account for 92.20% of the average.
def hour_weight(hour):
    if 6 <= hour < 24:
        return 0.9220 / 18  # 18 hours of "daytime" (06:00 - 24:00)
    else:
        return (1 - 0.9220) / 6  # 6 hours of "nighttime" (24:00 - 06:00)

temp_rain_wind["hour"] = temp_rain_wind["datetime"].dt.hour
temp_rain_wind["weight"] = temp_rain_wind["hour"].apply(hour_weight)

# Weighted temperature calculation
temp_rain_wind["weighted_temp"] = temp_rain_wind["T"] * temp_rain_wind["weight"]

# For investigating wind effects, the average wind speed (FH) is compared to a wind speed threshold which indicates stormy winds.
wind_threshold = 10 # in m/s

# Add a new column for hours where FH > threshold.
temp_rain_wind["high_wind"] = temp_rain_wind["FH"] > wind_threshold

# Values per month: 
# The weighted temperature average per month is calculated by dividing the total sum of the weighted temperatures in a month by the total weighted average sum.
# The total rain per hour is summed for each month to get the total monthly value.
# The total hours with high windspeeds per month is calculated by taking the sum of all windspeed hours above the threshold.
monthly_temp_rain = (
    temp_rain_wind.groupby(temp_rain_wind["datetime"].dt.to_period("M"))
    .apply(lambda g: pd.Series({
        "avg_weighted_temp": g["weighted_temp"].sum() / g["weight"].sum(),
        "total_precip": g["RH"].sum(),
        "hours_high_wind": g["high_wind"].sum()
    }))
    .reset_index()
)

# Convert the datetime which consists of periods back to timestamps to be able to plot later on.
monthly_temp_rain["month"] = monthly_temp_rain["datetime"].dt.to_timestamp()

# Merge both datasets of disruption and temperature/rain/wind together to make the plot. It looks for the columns "month" in both datasets which are then combined.
# 'inner' ensures only months will be kept that both have disruption and weather data. 
monthly_count_combined = pd.merge(monthly_count, monthly_temp_rain, on="month", how="inner")
monthly_minutes_combined = pd.merge(monthly_minutes, monthly_temp_rain, on="month", how="inner")



# Now, plots can be created to compare the weather data with the disruptions
fig, axs = plt.subplots(3, 2, figsize=(20, 18))
axs = axs.flatten()  # flatten the 3x2 array of axes for easy indexing


# Plot of the disruptions per month, together with the average weighted temperature in each month. 
ax1 = axs[0]

# Bar chart: number of disruptions (first axis)
ax1.bar(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["disruption_number"], label="Number of Disruptions", alpha=0.7)
ax1.set_xlabel("Month")
ax1.set_ylabel("Number of Disruptions")
ax1.grid(axis="y", linestyle="--", alpha=0.7)

# Line: temperature (second axis)
ax2 = ax1.twinx()
ax2.plot(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["avg_weighted_temp"], color="red", marker="o", label="Avg Temp (°C)")
ax2.set_ylabel("Average Temperature (°C)")

# Title and layout
ax1.set_title("Figure 1: Train Disruptions And Weighted Average Temperature Per Month (2024)")

# Add legends for both axes
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")



# Plot of the disruption minutes per month, together with the average weighted temperature in each month. 
ax3 = axs[1]

# Bar chart: disruption minutes (first axis)
ax3.bar(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["disruption_minutes"], label="Disruption Minutes", alpha=0.7)
ax3.set_xlabel("Month")
ax3.set_ylabel("Disruption Minutes")
ax3.grid(axis="y", linestyle="--", alpha=0.7)

# Line: temperature (second axis)
ax4 = ax3.twinx()
ax4.plot(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["avg_weighted_temp"], color="red", marker="o", label="Avg Temp (°C)")
ax4.set_ylabel("Average Temperature (°C)")

# Title and layout
ax3.set_title("Figure 2: Train Disruption Minutes And Weighted Average Temperature Per Month (2024)")

# Add legends for both axes
ax3.legend(loc="upper left")
ax4.legend(loc="upper right")



# Plot of the disruptions per month, together with the total rainfall in each month.
ax5 = axs[2]

# Bar chart: number of disruptions (first axis)
ax5.bar(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["disruption_number"], label="Number of Disruptions", alpha=0.7)
ax5.set_xlabel("Month")
ax5.set_ylabel("Number of Disruptions")
ax5.grid(axis="y", linestyle="--", alpha=0.7)

# Line: rainfall (second axis)
ax6 = ax5.twinx()
ax6.plot(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["total_precip"], color="blue", marker="s", label="Total Rainfall (mm)")
ax6.set_ylabel("Total Rainfall (mm)")

# Title and layout
ax5.set_title("Figure 3: Train Disruptions And Total Rainfall Per Month (2024)")

# Add legends for both axes
ax5.legend(loc="upper left")
ax6.legend(loc="upper right")



# Plot of the disruption minutes per month, together with the total rainfall in each month.
ax7 = axs[3]

# Bar chart: disruption minutes (first axis)
ax7.bar(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["disruption_minutes"], label="Disruption Minutes", alpha=0.7)
ax7.set_xlabel("Month")
ax7.set_ylabel("Disruption Minutes")
ax7.grid(axis="y", linestyle="--", alpha=0.7)

# Line: rainfall (second axis)
ax8 = ax7.twinx()
ax8.plot(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["total_precip"], color="blue", marker="s", label="Total Rainfall (mm)")
ax8.set_ylabel("Total Rainfall (mm)")

# Title and layout
ax7.set_title("Figure 4: Train Disruption Minutes And Total Rainfall Per Month (2024)")

# Add legends for both axes
ax7.legend(loc="upper left")
ax8.legend(loc="upper right")



# Plot of the disruption per month, together with the hourly windspeed frequency above the threshold in each month.
ax9 = axs[4]

# Bar chart: number of disruptions (first axis)
ax9.bar(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["disruption_number"],
         label="Number of Disruptions", alpha=0.7)
ax9.set_xlabel("Month")
ax9.set_ylabel("Number of Disruptions")
ax9.grid(axis="y", linestyle="--", alpha=0.7)

# Line: frequency of strong wind hours (second axis)
ax10 = ax9.twinx()
ax10.plot(monthly_count_combined["month"].dt.strftime("%b"), monthly_count_combined["hours_high_wind"], color="green", marker="^", label=f"Hours with FH > {wind_threshold*3.6:.0f} km/h")
ax10.set_ylabel(f"Hours with FH > {wind_threshold*3.6:.0f} km/h")

# Title and layout
ax9.set_title(f"Figure 5: Train Disruptions And Frequency of Mean Winds (> {wind_threshold*3.6:.0f} km/h) Per Month (2024)")

# Add legends for both axes
ax9.legend(loc="upper left")
ax10.legend(loc="upper right")



# Plot of the disruption minutes per month, together with the hourly windspeed frequency above the threshold in each month.
ax11 = axs[5]

# Bar chart: disruption minutes (first axis)
ax11.bar(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["disruption_minutes"],
        label="Disruption Minutes", alpha=0.7)
ax11.set_xlabel("Month")
ax11.set_ylabel("Disruption Minutes")
ax11.grid(axis="y", linestyle="--", alpha=0.7)

# Line: frequency of strong wind hours (second axis)
ax12 = ax11.twinx()
ax12.plot(monthly_minutes_combined["month"].dt.strftime("%b"), monthly_minutes_combined["hours_high_wind"], color="green", marker="^", label=f"Hours with FH > {wind_threshold*3.6:.0f} km/h")
ax12.set_ylabel(f"Hours with FH > {wind_threshold*3.6:.0f} km/h")

# Title and layout
ax11.set_title(f"Figure 6: Train Disruption Minutes And Frequency of Mean Winds (> {wind_threshold*3.6:.0f} km/h) Per Month (2024)")

# Add legends for both axes
ax11.legend(loc="upper left")
ax12.legend(loc="upper right")



# Final layout and display
plt.tight_layout()
plt.show()
