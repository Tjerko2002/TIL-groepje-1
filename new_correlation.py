import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import glob

# ========================
# 1. Load and prepare weather data (per station)
# ========================
files = sorted(glob.glob('data/df_train_weather_part*.csv'))
df_weather = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

df_weather['datetime'] = pd.to_datetime(df_weather['datetime'], errors='coerce')
df_weather = df_weather.dropna(subset=['datetime'])

weather_cols = [c for c in ['FH','FF','FX','T','T10N','Q','DR','RH','VV','M','R','S','O','Y']
                if c in df_weather.columns]

df_weather['block_day'] = df_weather['datetime'].dt.floor('D')

# Aggregate per station per day
df_weather_day = (
    df_weather
    .groupby(['rail_code','block_day'])[weather_cols]
    .mean()
    .reset_index()
)

# ========================
# 2. Load and prepare disruptions (expand station codes)
# ========================
df_disruptions = pd.read_csv('data/disruptions_filtered_top15_causes.csv')

df_disruptions['start_time'] = pd.to_datetime(df_disruptions['start_time'], errors='coerce')
df_disruptions['block_day'] = df_disruptions['start_time'].dt.floor('D')
df_disruptions['flag'] = 1

# Split multi-station field into lists
df_disruptions['rdt_station_codes'] = df_disruptions['rdt_station_codes'].str.replace(' ', '', regex=False)
df_disruptions['station_list'] = df_disruptions['rdt_station_codes'].str.split(',')

# Expand one row per station
df_disruptions_expanded = df_disruptions.explode('station_list').rename(columns={'station_list':'rail_code'})

# Aggregate per station per day per cause
df_disruption_day = (
    df_disruptions_expanded
    .pivot_table(
        index=['rail_code','block_day'],
        columns='cause_en',
        values='flag',
        aggfunc='sum',
        fill_value=0
    )
    .reset_index()
)

# ========================
# 3. Merge per-station weather + disruptions
# ========================
merged_day = pd.merge(df_weather_day, df_disruption_day, on=['rail_code','block_day'], how='inner')

# Standardize weather variables
scaler = StandardScaler()
merged_day[weather_cols] = scaler.fit_transform(merged_day[weather_cols])

# ========================
# 4. Correlation analysis
# ========================
all_cols = merged_day.columns.tolist()
disruption_cols = [c for c in all_cols if c not in weather_cols + ['block_day','rail_code']]

corr_matrix = merged_day.drop(columns=['block_day','rail_code']).corr(method='spearman')
corr_sub = corr_matrix.loc[weather_cols, disruption_cols]

# ========================
# 5. Plot heatmap
# ========================
plt.figure(figsize=(22, 12))
sns.heatmap(
    corr_sub,
    annot=True,
    fmt=".2f",
    cmap='coolwarm',
    linewidths=0.5
)
plt.title('Correlation between Local Daily Weather and Local Train Disruptions', fontsize=16)
plt.xlabel('Disruption Type')
plt.ylabel('Weather Variables')
plt.tight_layout()
plt.show()
