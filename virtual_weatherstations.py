import os
import numpy as np
import pandas as pd
from tqdm import tqdm   # <-- progress bar

# ---- helpers ----
def dist_km(lat1, lon1, lat2, lon2):
    lat1r = np.radians(lat1); lon1r = np.radians(lon1)
    lat2r = np.radians(lat2); lon2r = np.radians(lon2)
    dlat = lat2r - lat1r
    dlon = lon2r - lon1r
    ref = (lat1r + lat2r) / 2.0
    R = 6371.0
    dx = dlon * np.cos(ref) * R
    dy = dlat * R
    return np.sqrt(dx*dx + dy*dy)

def build_mapping(df_weather_meta, df_train_meta, radius_km=5.0, k=3):
    wm = df_weather_meta.rename(columns={'LAT(north)':'lat','LON(east)':'lon'})[['STN','lat','lon']]
    tm = df_train_meta.rename(columns={'code':'rail_code','geo_lat':'lat','geo_lng':'lon'})[['rail_code','lat','lon']]

    D = dist_km(tm['lat'].to_numpy()[:,None], tm['lon'].to_numpy()[:,None],
                wm['lat'].to_numpy()[None,:], wm['lon'].to_numpy()[None,:])

    rows = []
    for i in tqdm(range(len(tm)), desc="Mapping train→weather stations"):
        rail = tm.loc[i,'rail_code']
        dists = D[i]
        j_min = np.argmin(dists)
        if dists[j_min] <= radius_km:
            rows.append({'rail_code': rail, 'STN': wm.loc[j_min,'STN'], 'weight': 1.0})
        else:
            order = np.argsort(dists)[:k]
            inv = 1.0 / dists[order]
            w = inv / inv.sum()
            for stn, wv in zip(wm.loc[order,'STN'], w):
                rows.append({'rail_code': rail, 'STN': stn, 'weight': wv})
    return pd.DataFrame(rows)

def apply_mapping(df_weather, mapping, weather_cols):
    joined = df_weather.merge(mapping, on='STN', how='inner')
    for c in weather_cols:
        joined[c] = joined[c] * joined['weight']
    return joined.groupby(['datetime','rail_code'], as_index=False)[weather_cols].sum()

# ---- main ----
df_weather = pd.read_parquet(r"data\df_weather_5_stations.parquet")
df_weather['datetime'] = pd.to_datetime(df_weather['YYYYMMDD'].astype(str), format='%Y%m%d') \
                         + pd.to_timedelta(df_weather['HH'], unit='h')

df_train_meta = pd.read_csv(r"data\stations_within_circle.csv")
df_weather_meta = pd.read_csv(r"data\locations_weatherstations.csv")

weather_cols = [c for c in ['FH','FF','FX','T','T10N','Q','DR','RH','VV','M','R','S','O','Y'] if c in df_weather.columns]

mapping = build_mapping(df_weather_meta, df_train_meta, radius_km=5.0, k=3)
df_train_weather = apply_mapping(df_weather, mapping, weather_cols)

print(df_train_weather.head())

# assume df_train_weather already exists
n = len(df_train_weather)
parts = np.array_split(df_train_weather, 4)

for i, part in enumerate(parts, start=1):
    part.to_csv(fr"data\df_train_weather_part{i}.csv", index=False)

