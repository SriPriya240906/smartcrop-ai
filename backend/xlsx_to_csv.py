import pandas as pd

df = pd.read_excel("final crop reduced.xlsx")
df.to_csv("final_crop_reduced.csv", index=False, encoding="utf-8")

print("CSV created successfully")
