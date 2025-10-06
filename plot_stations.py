import geopandas
import matplotlib.pyplot as plt
import contextily as ctx

# 1. Convert the pandas DataFrame to a GeoDataFrame
gdf = geopandas.GeoDataFrame(
    df_stations, geometry=geopandas.points_from_xy(df['LON(east)'], df['LAT(north)'])
)
# Set the coordinate reference system to WGS84 (standard for GPS)
gdf.set_crs(epsg=4326, inplace=True)

# 2. Create a plot
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# 3. Plot the stations
gdf.plot(ax=ax, color='blue', markersize=40)

# Add labels for each point
for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf['NAME']):
    ax.text(x, y, label, fontsize=9, ha='right')

# 4. Add a basemap for context
ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
ax.set_title("Weather Stations in the Netherlands")
plt.show()