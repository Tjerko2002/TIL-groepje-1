import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

#########################################################################
## Correlations per hour 
#########################################################################

# Loading weather data
df_weather = pd.read_csv('data/df_weather_2024.csv')

# HH as string. 
df_weather['HH'] = df_weather['HH'].astype(str).str.zfill(2)

# Merge YYYYMMDD and HH to datetime string
df_weather['datetime_str'] = df_weather['YYYYMMDD'].astype(str) + df_weather['HH']

# filter for correct rows
df_weather = df_weather[df_weather['datetime_str'].str.len() == 10]

# change to datetime
df_weather['datetime'] = pd.to_datetime(
    df_weather['datetime_str'], 
    format='%Y%m%d%H', 
    errors='coerce'
)

# Eventuele mislukte conversies eruit
df_weather = df_weather.dropna(subset=['datetime'])

# Select relevant columns
weather_cols = ['FH','FF','FX','T','Q','DR','RH','VV','M','R','S','O','Y']
df_weather_sel = df_weather[['datetime'] + weather_cols].copy()

# Correct units
for col in ['FH','FF','FX','T','RH','DR']:
    df_weather_sel[col] = df_weather_sel[col] / 10

# Load disruptions
df_disruptions = pd.read_csv('data/disruptions_filtered_selected_causes.csv')

# Unify start times. 
df_disruptions['start_time'] = pd.to_datetime(df_disruptions['start_time'])
df_disruptions['datetime'] = df_disruptions['start_time'].dt.floor('H')

# Create pivot table of the disruptions. 
df_disruptions['flag'] = 1
df_disruption_pivot = (
    df_disruptions
    .pivot_table(
        index='datetime',
        columns='statistical_cause_en',
        values='flag',
        aggfunc='sum',        # number of disruptions per hour per type
        fill_value=0
    )
    .reset_index()
)

# Merge weather and disruptions
merged = pd.merge(df_weather_sel, df_disruption_pivot, on='datetime', how='inner')

# Convert to z-scores
scaler = StandardScaler()
merged[weather_cols] = scaler.fit_transform(merged[weather_cols])


# Correlation calculations
all_cols = merged.columns.tolist()
disruption_cols = [c for c in all_cols if c not in weather_cols + ['datetime']]

# Spearman correlation 
corr_matrix = merged.drop(columns=['datetime']).corr(method='spearman')

# Weather vs disruption in the matrix.
corr_sub = corr_matrix.loc[weather_cols, disruption_cols]

# Plot the heatmap
plt.figure(figsize=(18, 10))
sns.heatmap(
    corr_sub,
    annot=True,
    fmt=".2f",
    cmap='coolwarm',
    linewidths=0.5
)
plt.title('Correlation between Hourly Weather Conditions and Train Disruptions', fontsize=16)
plt.xlabel('Disruption Type')
plt.ylabel('Weather Variables')
plt.tight_layout()
plt.show()

#########################################################################
## Correlations per day 
#########################################################################


# 1. Load and prepare weather data
df_weather = pd.read_csv('data/df_weather_2024.csv')

# Format hour and create datetime
df_weather['HH'] = df_weather['HH'].astype(str).str.zfill(2)
df_weather['datetime_str'] = df_weather['YYYYMMDD'].astype(str) + df_weather['HH']
df_weather = df_weather[df_weather['datetime_str'].str.len() == 10]
df_weather['datetime'] = pd.to_datetime(df_weather['datetime_str'], format='%Y%m%d%H', errors='coerce')
df_weather = df_weather.dropna(subset=['datetime'])

# Weather columns
weather_cols = ['FH','FF','FX','T','Q','DR','RH','VV','M','R','S','O','Y']
df_weather_sel = df_weather[['datetime'] + weather_cols].copy()

# Convert units where needed
for col in ['FH','FF','FX','T','RH','DR']:
    if col in df_weather_sel.columns:
        df_weather_sel[col] = df_weather_sel[col] / 10

# Create daily blocks
df_weather_sel['block_day'] = df_weather_sel['datetime'].dt.floor('D')

# Aggregate weather per day (mean values)
df_weather_day = df_weather_sel.groupby('block_day')[weather_cols].mean().reset_index()

# ========================
# 2. Load and prepare disruptions
# ========================
df_disruptions = pd.read_csv('data/disruptions_filtered_selected_causes.csv')
df_disruptions['start_time'] = pd.to_datetime(df_disruptions['start_time'])
df_disruptions['block_day'] = df_disruptions['start_time'].dt.floor('D')
df_disruptions['flag'] = 1

# Count disruptions per day per cause
df_disruption_day = (
    df_disruptions
    .pivot_table(
        index='block_day',
        columns='statistical_cause_en',
        values='flag',
        aggfunc='sum',
        fill_value=0
    )
    .reset_index()
)

# 3. Merge weather and disruptions
merged_day = pd.merge(df_weather_day, df_disruption_day, on='block_day', how='inner')

# Standardize weather variables
scaler = StandardScaler()
merged_day[weather_cols] = scaler.fit_transform(merged_day[weather_cols])

# 4. Correlation analysis
all_cols = merged_day.columns.tolist()
disruption_cols = [c for c in all_cols if c not in weather_cols + ['block_day']]

# Spearman correlation
corr_matrix_day = merged_day.drop(columns=['block_day']).corr(method='spearman')
corr_sub_day = corr_matrix_day.loc[weather_cols, disruption_cols]

# 5. Plot heatmap
plt.figure(figsize=(22, 12))
sns.heatmap(
    corr_sub_day,
    annot=True,
    fmt=".2f",
    cmap='coolwarm',
    linewidths=0.5
)
plt.title('Correlation between Daily Weather Conditions and Train Disruptions', fontsize=16)
plt.xlabel('Disruption Type')
plt.ylabel('Weather Variables')
plt.tight_layout()
plt.show()
