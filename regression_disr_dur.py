# df_weather = pd.read_parquet(os.path.join(os.getcwd(), r"data\df_weather_5_stations.parquet"))
# df_stations = pd.read_csv(os.path.join(os.getcwd(), r"data\stations_within_circle.csv"))
# df_disruptions = pd.read_parquet(os.path.join(os.getcwd(), r"data\disruptions_withincircle.parquet"))

# ============================
# Correlate WEATHER ↔ DURATION
# ============================
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
#from statsmodels.stats.multitest import multipletests

# ----------------------------
# 0) CONFIG
# ----------------------------
PATH_WEATHER = os.path.join(os.getcwd(), r"data\df_weather_5_stations.parquet")
PATH_DISRUPT = os.path.join(os.getcwd(), r"data\disruptions_withincircle.parquet")
WEATHER_STATION_FILTER = None   # e.g., 344 to select one station, or None to keep all

# KNMI-like weather columns present in your data
weather_cols = ['FH','FF','FX','T','T10N','Q','DR','RH','VV','M','R','S','O','Y']

# ----------------------------
# 1) LOAD + CLEAN WEATHER
# ----------------------------
df_weather = pd.read_parquet(PATH_WEATHER)

# Ensure hour is two digits and combine with date
df_weather['HH'] = df_weather['HH'].astype(str).str.zfill(2)
df_weather['datetime_str'] = df_weather['YYYYMMDD'].astype(str) + df_weather['HH']
df_weather = df_weather[df_weather['datetime_str'].str.len() == 10]

# Robust datetime parse
df_weather['datetime'] = pd.to_datetime(
    df_weather['datetime_str'], format='%Y%m%d%H', errors='coerce'
)
df_weather = df_weather.dropna(subset=['datetime'])

# Select only the relevant columns + datetime
keep_cols = ['datetime'] + [c for c in weather_cols if c in df_weather.columns]
df_weather_sel = df_weather[keep_cols].copy()

# Unit corrections (KNMI: /10 on these)
for col in ['FH','FF','FX','T','RH','DR']:
    if col in df_weather_sel.columns:
        df_weather_sel[col] = df_weather_sel[col] / 10.0

# ----------------------------
# 2) LOAD DISRUPTIONS
# ----------------------------
df_disruptions = pd.read_parquet(PATH_DISRUPT)

# Parse times and floor to hour (start time)
df_disruptions['start_time'] = pd.to_datetime(df_disruptions['start_time'])
df_disruptions['datetime'] = df_disruptions['start_time'].dt.floor('H')

# ----------------------------
# 3) PIVOT to DURATION per HOUR per CAUSE
# ----------------------------
# Sum total minutes of disruption per cause per hour
df_pivot_dur = (
    df_disruptions
    .pivot_table(
        index='datetime',
        columns='cause_en',           # adjust if you prefer "cause_group"
        values='duration_minutes',
        aggfunc='sum',
        fill_value=0
    )
    .reset_index()
)

# ----------------------------
# 4) MERGE WEATHER + DURATION
# ----------------------------
# Use inner join to keep overlapping timestamps only
merged = pd.merge(df_weather_sel, df_pivot_dur, on='datetime', how='inner').fillna(0)

# Drop columns with no variation (constant) to avoid nan correlations
constant_cols = [c for c in merged.columns if c != 'datetime' and merged[c].nunique() <= 1]
if constant_cols:
    merged = merged.drop(columns=constant_cols)
    weather_cols = [c for c in weather_cols if c in merged.columns]  # keep only remaining
# Identify disruption columns (all non-weather, non-datetime)
disruption_cols = [c for c in merged.columns if c not in set(weather_cols + ['datetime'])]

# ----------------------------
# 5) SPEARMAN r + p-values
# ----------------------------
corrs = pd.DataFrame(index=weather_cols, columns=disruption_cols, dtype=float)
pvals = pd.DataFrame(index=weather_cols, columns=disruption_cols, dtype=float)

for w in weather_cols:
    for d in disruption_cols:
        r, p = spearmanr(merged[w], merged[d])
        corrs.loc[w, d] = r
        pvals.loc[w, d] = p

# ----------------------------
# 6) (Optional) MULTIPLE TESTING CORRECTION (FDR)
# ----------------------------
use_fdr = False
if use_fdr:
    flat = pvals.values.flatten()
    ok = ~np.isnan(flat)
    adj = np.full_like(flat, np.nan, dtype=float)
    if ok.sum() > 0:
        _, p_adj, _, _ = multipletests(flat[ok], alpha=0.05, method='fdr_bh')
        adj[ok] = p_adj
    pvals_adj = pd.DataFrame(adj.reshape(pvals.shape), index=pvals.index, columns=pvals.columns)
    sig_mask = (pvals_adj >= 0.05) | np.isnan(pvals_adj)   # True = mask (hide) non-significant
    title_suffix = " (FDR, q<0.05)"
else:
    sig_mask = (pvals >= 0.05) | np.isnan(pvals)           # True = mask (hide) non-significant
    title_suffix = " (p<0.05)"

# ----------------------------
# 7) HEATMAP
# ----------------------------
plt.figure(figsize=(18, 10))
sns.heatmap(
    corrs,
    mask=sig_mask,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    linewidths=0.5,
    cbar_kws={"label": "Spearman ρ"}
)
plt.title(f"Correlation: Weather vs Total Disruption Duration per Hour{title_suffix}", fontsize=16)
plt.xlabel("Disruption Type (duration minutes per hour)")
plt.ylabel("Weather Variables")
plt.tight_layout()
plt.show()

# ----------------------------
# 8) (Optional) CLUSTERED VIEW for pattern discovery
# ----------------------------
# Uncomment to see clustered structure (values still shown regardless of significance)
g = sns.clustermap(
    corrs,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    linewidths=0.4,
    figsize=(18, 10)
)
g.fig.suptitle("Clustermap: Weather vs Duration Correlations (unmasked)", y=1.02, fontsize=16)
plt.show()
