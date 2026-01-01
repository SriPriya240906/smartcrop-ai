import pandas as pd

df = pd.read_csv("final_crop_reduced.csv", encoding="latin1")

print("Loaded successfully")
print("Rows, Columns:", df.shape)
print("Columns:", df.columns.tolist())
print("Soil types:", df["soil_type"].unique())
print("Crops:", df["label"].unique())
