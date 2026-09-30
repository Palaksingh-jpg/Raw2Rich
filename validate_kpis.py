import pandas as pd
df = pd.read_csv("superstore_cleaned.csv")
print("Total Sales:", df["sales"].sum())
print("Total Profit:", df["profit"].sum())
print("Total Quantity:", df["quantity"].sum())
print("Total Orders:", df["order_id"].nunique())