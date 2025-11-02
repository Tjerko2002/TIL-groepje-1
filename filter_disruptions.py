import pandas as pd
import os

# Load both disruption data as well as the train stations within the circle.
df_disruptions = pd.read_csv(os.path.join(os.getcwd(), r"data\disruptions-2024 (3).csv"))
df_stations = pd.read_csv(os.path.join(os.getcwd(), r"data\stations_within_circle.csv"))

# Filter to only keep the disruptions from the disruption dataset that include at least
# one of the stations in the defined circle.
station_codes = set(df_stations["code"])

df = df_disruptions[
    df_disruptions["rdt_station_codes"].apply(
        lambda x: any(code.strip() in station_codes for code in str(x).split(","))
    )
].reset_index(drop=True)

# create new dataframe without the HSL entries
df = df[~df["rdt_lines"].str.contains("HSL", na=False)]

# Define the causes to keep for analysis and create new dataframe with disruptions.
chosen_causes = [
    "broken down train",
    "signal failure",
    "damaged overhead wires",
    "defective railway track",
    "damaged railway bridge",
    "stranded train",
    "level crossing failure",
    "an object in the overhead wires",
    "defective point",
    "damaged level crossing"
]

df_filtered = df[df["statistical_cause_en"].isin(chosen_causes)].reset_index(drop=True)

# Count and display the frequency of these causes.
statcause_count_filtered = df_filtered["statistical_cause_en"].value_counts()
print("Frequency of selected disruption causes:")
print(statcause_count_filtered)

# Export the filtered dataset
output_path = os.path.join(os.getcwd(), "data", "disruptions_filtered_selected_causes.csv")
df_filtered.to_csv(output_path, index=False, encoding="utf-8")

print(f"\nFiltered dataset saved to: {output_path}")
