import pandas as pd

# Load cleaned inventory dataset
df = pd.read_csv("data/clean_inventory.csv")

print("\n===== INVENTORY DATA VALIDATION =====")

print("\nRows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATES ---")
print(df.duplicated().sum())

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- FIRST 5 RECORDS ---")
print(df.head())

print("\n===== INVENTORY VALIDATION COMPLETE =====")