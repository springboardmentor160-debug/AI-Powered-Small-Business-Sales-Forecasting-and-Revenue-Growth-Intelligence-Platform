import pandas as pd

sales = pd.read_csv("data/clean_retail_sales.csv")
customers = pd.read_csv("data/clean_customers.csv")
products = pd.read_csv("data/clean_products.csv")

print("\n===== SALES DATA =====")
print("Rows:", len(sales))
print("Columns:", len(sales.columns))
print("Missing values:", sales.isnull().sum().sum())
print("Duplicates:", sales.duplicated().sum())

print("\n===== CUSTOMER DATA =====")
print("Rows:", len(customers))
print("Columns:", len(customers.columns))
print("Missing values:", customers.isnull().sum().sum())
print("Duplicates:", customers.duplicated().sum())

print("\n===== PRODUCT DATA =====")
print("Rows:", len(products))
print("Columns:", len(products.columns))
print("Missing values:", products.isnull().sum().sum())
print("Duplicates:", products.duplicated().sum())

print("\n===== VALIDATION COMPLETE =====")