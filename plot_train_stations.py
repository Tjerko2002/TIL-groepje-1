
# Code to plot the train stations without the weather stations
# import pandas as pd
# import os
# import plotly.express as px

# # 1. Load CSV file
# filename = 'data/stations-2023-09.csv'
# file_path = os.path.join(os.getcwd(), filename)
# df = pd.read_csv(file_path)
# print(df.head())

# # Initializing variables
# lat_col = 'geo_lat'
# lon_col = 'geo_lng'
# name_col = 'name_long'        
# id_col = 'id'           

# # Create a plotly map of the dataframe 
# fig = px.scatter_mapbox(
#     df,
#     lat=lat_col,
#     lon=lon_col,
#     hover_name=name_col,           
#     hover_data=[id_col],           
#     color_discrete_sequence=["red"],  
#     zoom=7,
#     title="Train Stations in the Netherlands"
# )

# # 4. Layout of the map
# fig.update_layout(
#     mapbox_style="open-street-map",
#     margin={"r":0, "t":40, "l":0, "b":0}
# )

# fig.show()




# Code to plot the train stations with the weather stations included
import pandas as pd
import os
import plotly.graph_objects as go # Import graph_objects

# --- 1. Load and Prepare Data ---
df_stations = pd.read_parquet(os.path.join(os.getcwd(),r"data\df_stations.parquet"))


# Load train station data
filename = 'data/stations-2023-09.csv'
file_path = os.path.join(os.getcwd(), filename)
df_train = pd.read_csv(file_path) # Renamed to df_train for clarity


# --- 2. Create the Figure and Add Traces ---

# Initialize a figure using graph_objects
fig = go.Figure()

# Add the first trace: Weather Stations (Blue)
fig.add_trace(go.Scattermapbox(
    lat=df_stations['LAT(north)'],
    lon=df_stations['LON(east)'],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=10,
        color='blue'
    ),
    hoverinfo='text',
    text=df_stations['NAME'], # Text that appears on hover
    name='Weather Stations'   # Name for the legend
))

# Add the second trace: Train Stations (Red)
fig.add_trace(go.Scattermapbox(
    lat=df_train['geo_lat'],
    lon=df_train['geo_lng'],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=5,
        color='red'
    ),
    hoverinfo='text',
    text=df_train['name_long'],
    name='Train Stations'
))


# --- 3. Update the Layout ---

fig.update_layout(
    title='Weather and Train Stations in the Netherlands',
    mapbox_style="open-street-map",
    mapbox_zoom=7,
    # Center the map on the Netherlands
    mapbox_center={"lat": 52.3, "lon": 5.5},
    margin={"r":0, "t":40, "l":0, "b":0},
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

# --- 4. Show the Figure ---
fig.show()