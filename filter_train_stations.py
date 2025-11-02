import pandas as pd
from geopy.distance import geodesic
import os

# control current working map
print("Current working directory:", os.getcwd())

#Rea d staions data
df = pd.read_csv('data/stations-2023-09.csv')

#centre of circle — Bodegraven
center_lat = 52.0822
center_lon = 4.7447
radius_km = 40  # Straal in kilometers

# Is the station in the circle
def within_radius(row):
    station_loc = (row['geo_lat'], row['geo_lng'])
    center_loc = (center_lat, center_lon)
    distance = geodesic(center_loc, station_loc).km
    return distance <= radius_km

#Filter stations within the circle
df_circle = df[df.apply(within_radius, axis=1)]

# save as CSV
output_path = 'data/stations_within_circle.csv'
df_circle.to_csv(output_path, index=False)

#  show results
print(f"{len(df_circle)} stations found within {radius_km} km from Bodegraven.")
df_circle.head()