import pandas as pd
import os

df_disruptions = pd.read_csv(os.path.join(os.getcwd(),r"data\disruptions-2024 (3).csv"))
df_stations = pd.read_csv(os.path.join(os.getcwd(),r"data\stations_within_circle.csv"))

# create a set of the station codes within the circle
station_codes = set(df_stations["code"])

# keep only rows where at least one code in rdt_station_codes is in the station list
df = df_disruptions[
    df_disruptions["rdt_station_codes"].apply(
        lambda x: any(code.strip() in station_codes for code in str(x).split(","))
    )
].reset_index(drop=True)

df_filtered = df[~df["rdt_lines"].str.contains("HSL", na=False)]

print(df_filtered.head(20))

# save filtered disruptions as parquet
df_filtered.to_parquet(os.path.join(os.getcwd(),r"data\disruptions_withincircle.parquet"))
