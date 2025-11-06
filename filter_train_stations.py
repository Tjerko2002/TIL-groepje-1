import pandas as pd
from geopy.distance import geodesic
import os
"This document opens all the trainstations, and only keeps the ones within 40km from Bodegraven."

#Read staions data
df = pd.read_csv('data/stations-2023-09.csv')

# Define centre of circle — Bodegraven
center_lat = 52.0822
center_lon = 4.7447
radius_km = 40

# Uses geodesic to calculate the distance between Bodegraven and the trainstation.
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