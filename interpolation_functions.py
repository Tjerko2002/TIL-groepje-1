import pandas as pd
from geopy.distance import geodesic
import numpy as np
import os

# 1. Sample DataFrame with station locations and weather data
#    (Replace with your actual DataFrame)
data = {
    'STN': [215, 235, 240, 249, 251, 260, 267],
    'LON(east)': [4.437, 4.781, 4.790, 4.979, 5.346, 5.180, 5.384],
    'LAT(north)': [52.141, 52.928, 52.318, 52.644, 53.392, 52.100, 52.898],
    'NAME': ['Voorschoten', 'De Kooy', 'Schiphol', 'Berkhout', 'Hoorn Terschelling', 'De Bilt', 'Stavoren'],
    'Temperature_C': [15.2, 14.8, 15.5, 14.9, 14.1, 15.6, 14.5],
    'Wind_Speed_kmh': [22, 28, 25, 26, 35, 19, 30]
}
df_stations = pd.DataFrame(data)




def find_closest_stations(input_lat, input_lon, stations_df):
    """Finds the 3 closest weather stations to a given lat/lon point."""
    input_location = (input_lat, input_lon)
    
    distances = stations_df.apply(
        lambda row: geodesic(input_location, (row['LAT(north)'], row['LON(east)'])).km,
        axis=1
    )
    
    df_with_dist = stations_df.copy()
    df_with_dist['distance_km'] = distances
    
    return df_with_dist.sort_values('distance_km').head(3)


def get_weighted_average_weather(closest_stations_df):
    """
    Calculates the weighted average of weather data from the closest stations
    using Inverse Distance Weighting (IDW).
    
    Returns:
        A dictionary with the interpolated weather data.
    """
    # Handle the edge case where the location is exactly at a station
    if closest_stations_df['distance_km'].iloc[0] < 0.01: # less than 10 meters
        # Return the data from the first station directly
        first_station = closest_stations_df.iloc[0]
        weather_cols = ['Temperature_C', 'Wind_Speed_kmh'] # Define weather columns
        return first_station[weather_cols].to_dict()

    # Calculate inverse distance weights
    weights = 1 / closest_stations_df['distance_km']
    sum_of_weights = np.sum(weights)
    
    weighted_averages = {}
    
    # Iterate through the weather data columns to calculate the weighted average
    weather_cols_to_average = ['Temperature_C', 'Wind_Speed_kmh']
    
    for col in weather_cols_to_average:
        weighted_sum = np.sum(closest_stations_df[col] * weights)
        weighted_average = weighted_sum / sum_of_weights
        weighted_averages[col] = weighted_average
        
    return weighted_averages


# --- EXAMPLE USAGE ---

# 1. Manually enter a location (e.g., Rotterdam Centraal)
my_lat = 51.9225
my_lon = 4.47917

# 2. Find the 3 closest stations
closest_stations = find_closest_stations(my_lat, my_lon, df_stations)

print("The 3 closest stations to your location are:")
print(closest_stations[['NAME', 'STN', 'distance_km', 'Temperature_C', 'Wind_Speed_kmh']])
print("-" * 50)

# 3. Calculate and display the interpolated weather data for that location
interpolated_weather = get_weighted_average_weather(closest_stations)

print("Interpolated weather data for your location:")
print(f"Estimated Temperature: {interpolated_weather['Temperature_C']:.2f}°C")
print(f"Estimated Wind Speed: {interpolated_weather['Wind_Speed_kmh']:.2f} km/h")