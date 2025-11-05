# Code to plot the train stations with the weather stations included
import pandas as pd
import os
import plotly.graph_objects as go # Import graph_objects

# 1. Load and Prepare Data
df_stations = pd.read_csv(os.path.join(os.getcwd(),r"data\df_weatherstations_locations.csv"))


# Load train station data
filename = 'data/stations-2023-09.csv'
file_path = os.path.join(os.getcwd(), filename)
df_train = pd.read_csv(file_path) # Renamed to df_train for clarity


# 2. Create the Figure and Add Traces

# Initialize a figure using graph_objects
fig = go.Figure()

# Add the first trace: Weather Stations (Blue)
fig.add_trace(go.Scattermap(
    lat=df_stations['LAT(north)'],
    lon=df_stations['LON(east)'],
    mode='markers',
    marker=dict(size=10, color='blue'),
    hoverinfo='text',
    text=df_stations['NAME'], # Text that appears on hover
    name='Weather Stations'   # Name for the legend
))

# Add the second trace: Train Stations (Red)
fig.add_trace(go.Scattermap(
    lat=df_train['geo_lat'],
    lon=df_train['geo_lng'],
    mode='markers',
    marker=dict(size=5, color='red'),
    hoverinfo='text',
    text=df_train['name_long'],
    name='Train Stations'
))


# 3. Update the Layout

fig.update_layout(
    title='Weather and Train Stations in the Netherlands',
    map=dict(
        style="open-street-map",
        center=dict(lat=52.3, lon=5.5),
        zoom=7,
    ),
    margin=dict(r=0, t=40, l=0, b=0),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)
# 4. Show the Figure
fig.show()