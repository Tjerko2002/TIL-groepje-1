import pandas as pd
import os 


filename= 'data/disruptions-2024 (3).csv'
file_path = os.path.join(os.getcwd(),filename)
print(file_path)
df = pd.read_csv(file_path)
df.head(50)
df["ns_lines"].value_counts()

df_new = df.groupby("ns_lines")
df_new.get_group("Rotterdam-Breda (HSL)")