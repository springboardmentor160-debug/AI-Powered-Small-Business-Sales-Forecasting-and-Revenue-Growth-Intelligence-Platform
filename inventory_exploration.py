import pandas as pd

df = pd.read_csv("data/Grocery_Inventory_and_Sales_Dataset.csv")

print("\n--- DATASET SHAPE ---")
print(df.shape)

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- FIRST 5 ROWS ---")
print(df.head())

print("\n--- DATASET INFO ---")
df.info()

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATE ROWS ---")
print(df.duplicated().sum())