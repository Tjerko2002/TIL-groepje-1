import pandas as pd
import os 

# Read the csv file that shows all train disruptions in 2024 and on which trajectory it happened
filename= 'data/disruptions-2024 (3).csv'
file_path = os.path.join(os.getcwd(),filename)
print(file_path)
df = pd.read_csv(file_path)
df.head(5)

# Counts how many times each ns line is visible in the dataframe
dd = df["ns_lines"].value_counts()

# Creates a group of all the ns_lines and gets the group for the most visible trajectory, which is "Rotterdam-Breda (HSL)"
df_new = df.groupby("ns_lines")
ff = df_new.get_group("Rotterdam-Breda (HSL)")
print(ff)