import pandas as pd

# Load the sales dataset
sales_df = pd.read_csv("data/raw/sales_data.csv")

print("\n========== FIRST 5 ROWS ==========")
print(sales_df.head())

print("\n========== DATASET INFORMATION ==========")
sales_df.info()

print("\n========== SUMMARY STATISTICS ==========")
print(sales_df.describe())

print("\n========== MISSING VALUES ==========")
print(sales_df.isnull().sum())

print("\n========== DUPLICATE ROWS ==========")
print("Duplicate rows:", sales_df.duplicated().sum())

print("\n========== COLUMN NAMES ==========")
print(sales_df.columns.tolist())

print("\n========== DATASET SIZE ==========")
print("Rows:", len(sales_df))
print("Columns:", len(sales_df.columns))