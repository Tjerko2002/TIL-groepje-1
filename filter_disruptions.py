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

# Remove the HSL entries from the dataset.
df_filtered = df[~df["rdt_lines"].str.contains("HSL", na=False)]

#Count the 15 most frequent statistical causes
statcause_count_filtered = df_filtered["statistical_cause_en"].value_counts()
top_15_statcauses_filtered = statcause_count_filtered.head(15)

# print(top_15_statcauses_filtered)

#Create a new DataFrame containing only rows with these causes
df_top15_causes = df_filtered[
    df_filtered["statistical_cause_en"].isin(top_15_statcauses_filtered.index)
].reset_index(drop=True)

#print(df_top15_causes)

# Determine where the new file will be displayed and what the name will be
output_path = os.path.join(os.getcwd(), "data", "disruptions_filtered_top15_causes.csv")

# Export the DataFrame to CSV (without the index column)
df_top15_causes.to_csv(output_path, index=False, encoding="utf-8")
