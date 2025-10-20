import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

from scipy.stats import spearmanr
import numpy as np
import pandas as pd


# ========================
# 1. Load and prepare weather data
# ========================
df_weather = pd.read_parquet('data/df_weather_5_stations.parquet')

# Format hour and create datetime
df_weather['HH'] = df_weather['HH'].astype(str).str.zfill(2)
df_weather['datetime_str'] = df_weather['YYYYMMDD'].astype(str) + df_weather['HH']
df_weather = df_weather[df_weather['datetime_str'].str.len() == 10]
df_weather['datetime'] = pd.to_datetime(df_weather['datetime_str'], format='%Y%m%d%H', errors='coerce')
df_weather = df_weather.dropna(subset=['datetime'])

# Weather columns
weather_cols = ['FH','FF','FX','T','T10N','Q','DR','RH','VV','M','R','S','O','Y']
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
df_disruptions = pd.read_csv('data/disruptions_filtered_top15_causes.csv')
df_disruptions['start_time'] = pd.to_datetime(df_disruptions['start_time'])
df_disruptions['block_day'] = df_disruptions['start_time'].dt.floor('D')
df_disruptions['flag'] = 1

# Count disruptions per day per cause
df_disruption_day = (
    df_disruptions
    .pivot_table(
        index='block_day',
        columns='cause_en',
        values='flag',
        aggfunc='sum',
        fill_value=0
    )
    .reset_index()
)

# ========================
# 3. Merge weather and disruptions
# ========================
merged_day = pd.merge(df_weather_day, df_disruption_day, on='block_day', how='inner')

# Standardize weather variables
scaler = StandardScaler()
merged_day[weather_cols] = scaler.fit_transform(merged_day[weather_cols])

# ========================
# 4. Correlation analysis
# ========================
all_cols = merged_day.columns.tolist()
disruption_cols = [c for c in all_cols if c not in weather_cols + ['block_day']]

# Spearman correlation
corr_matrix_day = merged_day.drop(columns=['block_day']).corr(method='spearman')
corr_sub_day = corr_matrix_day.loc[weather_cols, disruption_cols]

# ========================
# 5. Plot heatmap wow
# ========================
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


# Now we calculate the p-value for each individual correlation

# create a DataFrame with the same index and columns as the correlation submatrix
pval_matrix_day = pd.DataFrame(
    index=weather_cols,
    columns=disruption_cols,
    dtype=float
)

# Loop over each weather and disruption pair can calculate the p-value
for w in weather_cols:
    for d in disruption_cols:
        # Compute Spearman correlation and p-value
        rho, p = spearmanr(merged_day[w], merged_day[d])
        pval_matrix_day.loc[w, d] = p

# Create a new heatmap with the p-values
plt.figure(figsize=(22, 12))
sns.heatmap(
    pval_matrix_day,
    annot=True,
    fmt=".3f",
    cmap='viridis_r',
    linewidths=0.5
)
plt.title('P-values for Correlation between Daily Weather and Disruptions', fontsize=16)
plt.xlabel('Disruption Type')
plt.ylabel('Weather Variables')
plt.tight_layout()
plt.show()


# Next a heatmap is created which shows the correlations that contain a p-value < 0.05
mask = pval_matrix_day >= 0.05  # True for non-significant
plt.figure(figsize=(22, 12))
sns.heatmap(
    corr_sub_day,
    annot=True,
    fmt=".2f",
    cmap='coolwarm',
    linewidths=0.5,
    mask=mask
)
plt.title('Significant Spearman Correlations (p < 0.05)', fontsize=16)
plt.xlabel('Disruption Type')
plt.ylabel('Weather Variables')
plt.tight_layout()
plt.show()
