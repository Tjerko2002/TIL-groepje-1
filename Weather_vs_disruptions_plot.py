import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
"""This Py file combines weather factors and plots their relation with weather effected train disruptions"""
# Step 1: Load and clean weather data

df_weather = pd.read_csv(r'data\df_weather_2024.csv')

# Convert units
df_weather['FX'] = df_weather['FX'] / 10  # max gust (m/s)
df_weather['FH'] = df_weather['FH'] / 10  # hourly mean wind (m/s)
df_weather['T'] = df_weather['T'] / 10    # temperature (°C)

# Format datetime
df_weather['HH'] = df_weather['HH'].astype(str).str.zfill(2)
df_weather['datetime_str'] = df_weather['YYYYMMDD'].astype(str) + df_weather['HH']
df_weather = df_weather[df_weather['datetime_str'].str.len() == 10]
df_weather['datetime'] = pd.to_datetime(df_weather['datetime_str'], format='%Y%m%d%H', errors='coerce')
df_weather = df_weather.dropna(subset=['datetime'])

# Create hourly block
df_weather['block_hour'] = df_weather['datetime'].dt.floor('h')


# Step 2: Load and filter disruptions data

df_disruptions = pd.read_csv('data/disruptions_filtered_top15_causes.csv')
df_disruptions['start_time'] = pd.to_datetime(df_disruptions['start_time'])
df_disruptions['end_time'] = pd.to_datetime(df_disruptions['end_time'], errors='coerce')

# Create hourly block
df_disruptions['block_hour'] = df_disruptions['start_time'].dt.floor('h')

# Filter for weather-sensitive causes
included_causes = [
    'an object in the overhead wires',
    'broken down train',
    'demaged railway bridge',
    'defective railway track'
    'defective point',
    'hinderence on the railway',
    'level crossing failure',
    'signal failure',
    




]
df_disruptions = df_disruptions[
    df_disruptions['cause_en'].str.lower().isin(included_causes)
]

# Aggregate disruptions per hour
df_disruption_hour = (
    df_disruptions
    .groupby('block_hour')
    .agg(n_disruptions=('rdt_id', 'count'))
    .reset_index()
)


# Step 3: Classify hourly weather categories
def categorize_weather_hour(row):
    T = row['T']
    Q = row['Q']
    DR = row['DR']
    RH = row['RH']  
    FH = row['FH']
    FX = row['FX']
    S = row['S']    

    # Stormy hour: stronger wind and significant precipitation
    if (0 <= T <= 25) and (Q <= 100) and ((RH >= 5) or (DR >= 2)) and (FX >= 20 or FH >= 10):
        return 'Stormy hour'

    # Heat hour: hot, sunny, dry, low wind
    elif (T >= 28) and (Q >= 200) and (RH == 0) and (FX < 12) and (FH < 7):
        return 'Heat hour'

    # Cold or snowy hour: cold temperatures or snow present
    elif (T <= 0) or (S == 1):
        return 'Cold or snowy hour'

    # Neutral hour: mild conditions, no precipitation
    elif (8 <= T <= 22) and (Q <= 150) and (RH == 0) and (FX < 12) and (FH < 7):
        return 'Neutral hour'

    else:
        return 'Other hour'

df_weather['weather_category_hour'] = df_weather.apply(categorize_weather_hour, axis=1)

# Step 4: Merge hourly weather with disruptions

merged_hour = pd.merge(df_weather, df_disruption_hour, on='block_hour', how='left')
merged_hour['n_disruptions'] = merged_hour['n_disruptions'].fillna(0)


# Step 5: Count scenarios and aggregate disruptions

# filter only peak hours (e.g. 06:00 - 22:00)

merged_hour = merged_hour[
    (merged_hour['block_hour'].dt.hour >= 6) &
    (merged_hour['block_hour'].dt.hour <= 22)
]
print("\nHourly scenario distribution:")
print(merged_hour['weather_category_hour'].value_counts())

agg_hour = (
    merged_hour
    .groupby('weather_category_hour')
    .agg(
        avg_disruptions=('n_disruptions', 'mean'),
        hours_count=('n_disruptions', 'count')
    )
    .reset_index()
)

print("\nAverage disruptions per hourly weather category:")
print(agg_hour)



merged_hour.to_csv('data/merged_hour.csv')
print("merged_hour saved to data/merged_hour.csv")

# Step 6: Plot hourly disruptions per category

order_hour = ['Stormy hour', 'Neutral hour', 'Very cold hour', 'Heat hour', 'Other hour']



plt.figure(figsize=(8,5))
sns.barplot(data=agg_hour, x='weather_category_hour', y='avg_disruptions', order=order_hour, color='steelblue')
plt.title('Average disruptions per hourly weather category')
plt.ylabel('Average disruptions per hour')
plt.xlabel('Weather category')
plt.tight_layout()
plt.show()

