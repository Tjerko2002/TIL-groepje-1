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