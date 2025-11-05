import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr

#########################################################################
## Correlations and p-values per hour 
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

# Drop potential failed conversions
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
df_disruptions['datetime'] = df_disruptions['start_time'].dt.floor('h')

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
merged_hour = pd.merge(df_weather_sel, df_disruption_pivot, on='datetime', how='inner')

# Convert to z-scores
scaler = StandardScaler()
merged_hour[weather_cols] = scaler.fit_transform(merged_hour[weather_cols])


# Correlation calculations
all_cols = merged_hour.columns.tolist()
disruption_cols = [c for c in all_cols if c not in weather_cols + ['datetime']]

# Spearman correlation 
corr_matrix = merged_hour.drop(columns=['datetime']).corr(method='spearman')

# Weather vs disruption in the matrix.
corr_sub_hour = corr_matrix.loc[weather_cols, disruption_cols]

# Calculate the p-values 

# Create DataFrame with same index and columns as correlation matrix
pval_matrix_hour = pd.DataFrame(
    index=weather_cols,
    columns=disruption_cols,
    dtype=float
)

# Loop over each weather and disruption pair for p-value calculation
for w in weather_cols:
    for d in disruption_cols:
        # Compute Spearman correlation and p-value
        rho, p = spearmanr(merged_hour[w], merged_hour[d])
        pval_matrix_hour.loc[w, d] = p


#########################################################################
## Correlations and p-values per day 
#########################################################################


# Load and prepare weather data
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


# Load and prepare disruptions
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

# Merge weather and disruptions
merged_day = pd.merge(df_weather_day, df_disruption_day, on='block_day', how='inner')

# Standardize weather variables
scaler = StandardScaler()
merged_day[weather_cols] = scaler.fit_transform(merged_day[weather_cols])

# Correlation analysis
all_cols = merged_day.columns.tolist()
disruption_cols = [c for c in all_cols if c not in weather_cols + ['block_day']]

# Spearman correlation
corr_matrix_day = merged_day.drop(columns=['block_day']).corr(method='spearman')
corr_sub_day = corr_matrix_day.loc[weather_cols, disruption_cols]

# Calculate the p-values 

# Create DataFrame with same index and columns as correlation matrix
pval_matrix_day = pd.DataFrame(
    index=weather_cols,
    columns=disruption_cols,
    dtype=float
)

# Loop over each weather and disruption pair for p-value calculation
for w in weather_cols:
    for d in disruption_cols:
        # Compute Spearman correlation and p-value
        rho, p = spearmanr(merged_day[w], merged_day[d])
        pval_matrix_day.loc[w, d] = p


#########################################################################
## Correlation and p-value plots
#########################################################################

# Six figures showing the correlations, the corresponding p-values and the correlations with p-values < 0.05 in heatmaps for both hourly and daily level comparisons.
fig, axs = plt.subplots(3, 2, figsize=(36, 24))
axs = axs.flatten()  # flatten the 3x2 array for easy indexing


# Create the heatmap for the hourly level correlations
ax1 = axs[0]
sns.heatmap(
    corr_sub_hour,
    annot=True,
    fmt=".2f",
    cmap='coolwarm',
    linewidths=0.5,
    ax=ax1
)
ax1.set_title('Correlations between Hourly Weather Conditions and Train Disruptions', fontsize=16)
ax1.set_xlabel('Disruption Type')
ax1.set_ylabel('Weather Variables')


# Create the heatmap for the daily level correlations
ax2 = axs[1]
sns.heatmap(
    corr_sub_day,
    annot=True,
    fmt=".2f",
    cmap='coolwarm',
    linewidths=0.5,
    ax=ax2
)
ax2.set_title('Correlations between Daily Weather Conditions and Train Disruptions', fontsize=16)
ax2.set_xlabel('Disruption Type')
ax2.set_ylabel('Weather Variables')


# Create a heatmap with the p-values related to the hourly level correlations
ax3 = axs[2]
sns.heatmap(
    pval_matrix_hour,
    annot=True,
    fmt=".3f",
    cmap='viridis_r',
    linewidths=0.5,
    ax=ax3
)
ax3.set_title('P-values for Correlations between Hourly Weather and Disruptions', fontsize=16)
ax3.set_xlabel('Disruption Type')
ax3.set_ylabel('Weather Variables')


# Create a heatmap with the p-values related to the daily level correlations
ax4 = axs[3]
sns.heatmap(
    pval_matrix_day,
    annot=True,
    fmt=".3f",
    cmap='viridis_r',
    linewidths=0.5,
    ax=ax4
)
ax4.set_title('P-values for Correlations between Daily Weather and Disruptions', fontsize=16)
ax4.set_xlabel('Disruption Type')
ax4.set_ylabel('Weather Variables')


# Create a heatmap which shows the correlations with p-value < 0.05 related to the hourly level correlations
mask = pval_matrix_hour >= 0.05  # True for non-significant
ax5 = axs[4]
sns.heatmap(
    corr_sub_hour,
    annot=True,
    fmt=".2f",
    cmap='coolwarm',
    linewidths=0.5,
    mask=mask,
    ax=ax5
)
ax5.set_title('Statistically Significant Correlations (p < 0.05)', fontsize=16)
ax5.set_xlabel('Disruption Type')
ax5.set_ylabel('Weather Variables')


# Create a heatmap which shows the correlations with p-value < 0.05 related to the daily level correlations
mask = pval_matrix_day >= 0.05  # True for non-significant
ax6 = axs[5]
sns.heatmap(
    corr_sub_day,
    annot=True,
    fmt=".2f",
    cmap='coolwarm',
    linewidths=0.5,
    mask=mask,
    ax=ax6
)
ax6.set_title('Statistically Significant Correlations (p < 0.05)', fontsize=16)
ax6.set_xlabel('Disruption Type')
ax6.set_ylabel('Weather Variables')


# Final layout and display
plt.tight_layout()
plt.show()
