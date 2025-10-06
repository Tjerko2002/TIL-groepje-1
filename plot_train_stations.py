import pandas as pd
import os 
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point


filename= 'data/stations-2023-09.csv'
file_path = os.path.join(os.getcwd(),filename)
df = pd.read_csv(file_path)
#print(df.head(5))

geometry = [Point(xy) for xy in zip(df['geo_lng'], df['geo_lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry)

world = gpd.read_file("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json")
nl = world[world['name'] == "Netherlands"]


ax = nl.plot(color='lightgrey', edgecolor='black', figsize=(10,10))
gdf.plot(ax=ax, markersize=20, color='red', alpha=0.7)
plt.show()