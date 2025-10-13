# import pandas as pd
# import os 
# import geopandas as gpd
# import matplotlib.pyplot as plt
# from shapely.geometry import Point


# filename= 'data/stations-2023-09.csv'
# file_path = os.path.join(os.getcwd(),filename)
# df = pd.read_csv(file_path)
# #print(df.head(5))

# geometry = [Point(xy) for xy in zip(df['geo_lng'], df['geo_lat'])]
# gdf = gpd.GeoDataFrame(df, geometry=geometry)

# world = gpd.read_file("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json")
# nl = world[world['name'] == "Netherlands"]


# ax = nl.plot(color='lightgrey', edgecolor='black', figsize=(10,10))
# gdf.plot(ax=ax, markersize=20, color='red', alpha=0.7)
# plt.show()


import pandas as pd
import os
import plotly.express as px

# 1. Load CSV file
filename = 'data/stations-2023-09.csv'
file_path = os.path.join(os.getcwd(), filename)
df = pd.read_csv(file_path)
print(df.head())

# Initializing variables
lat_col = 'geo_lat'
lon_col = 'geo_lng'
name_col = 'name_long'        
id_col = 'id'           

# Create a plotly map of the dataframe 
fig = px.scatter_mapbox(
    df,
    lat=lat_col,
    lon=lon_col,
    hover_name=name_col,           
    hover_data=[id_col],           
    color_discrete_sequence=["red"],  
    zoom=7,
    title="Train Stations in the Netherlands"
)

# 4. Layout of the map
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0, "t":40, "l":0, "b":0}
)

fig.show()