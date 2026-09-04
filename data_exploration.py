import pandas as pd

df = pd.read_excel("data/Online Retail.xlsx")

print("\n--- FIRST 5 ROWS ---")
print(df.head())

print("\n--- DATASET SHAPE ---")
print(df.shape)

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- DATASET INFO ---")
df.info()

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATE ROWS ---")
print(df.duplicated().sum())

print("\n--- UNIQUE CUSTOMERS ---")
print(df["CustomerID"].nunique())

print("\n--- UNIQUE PRODUCTS ---")
print(df["StockCode"].nunique())

print("\n--- COUNTRIES ---")
print(df["Country"].nunique())

print("\n--- DATE RANGE ---")
print("Start:", df["InvoiceDate"].min())
print("End:", df["InvoiceDate"].max())

print("\n--- NEGATIVE QUANTITY ---")
print((df["Quantity"] < 0).sum())

print("\n--- NEGATIVE PRICE ---")
print((df["UnitPrice"] < 0).sum())