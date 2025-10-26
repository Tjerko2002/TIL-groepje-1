import pandas as pd
from scipy.stats import kruskal
import scikit_posthocs as sp

# --------------------------------------------------
# Load pre-processed data
# --------------------------------------------------
# Je kunt hier rechtstreeks het csv of parquet bestand inladen
# of eventueel het dataframe opslaan in je hoofdscript en hier opnieuw gebruiken.
merged_hour = pd.read_parquet('data/merged_hour.parquet')

# Controle
print("Unieke categorieën:")
print(merged_hour['weather_category_hour'].value_counts())

# --------------------------------------------------
# Kruskal–Wallis test
# --------------------------------------------------
groups = [
    merged_hour.loc[merged_hour['weather_category_hour'] == cat, 'n_disruptions']
    for cat in merged_hour['weather_category_hour'].unique()
]

stat, p_value = kruskal(*groups)

print("\n--- Kruskal–Wallis test ---")
print(f"Statistic: {stat:.4f}")
print(f"P-value: {p_value:.6f}")

if p_value < 0.05:
    print("Er is een significant verschil tussen ten minste één van de groepen.")
else:
    print("Geen significant verschil aangetoond.")

# --------------------------------------------------
# Dunn's post-hoc test
# --------------------------------------------------
posthoc = sp.posthoc_dunn(
    merged_hour,
    val_col='n_disruptions',
    group_col='weather_category_hour',
    p_adjust='bonferroni'
)

print("\n--- Dunn's post-hoc test (p-values) ---")
print(posthoc)
