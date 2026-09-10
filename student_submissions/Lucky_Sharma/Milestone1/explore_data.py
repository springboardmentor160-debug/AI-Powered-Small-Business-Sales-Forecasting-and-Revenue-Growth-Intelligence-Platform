import pandas as pd

datasets = {
    "Sales": "data/raw/sales.csv",
    "Customers": "data/raw/customers.csv",
    "Products": "data/raw/products.csv",
    "Inventory": "data/raw/inventory.csv",
}

for name, path in datasets.items():
    df = pd.read_csv(path)

    print("\n" + "=" * 60)
    print(f"{name.upper()} DATASET")
    print("=" * 60)
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nDuplicate rows:", df.duplicated().sum())
    print("\nFirst 5 rows:")
    print(df.head())

sales = pd.read_csv("data/raw/sales.csv")
sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce")
sales["unit_price"] = pd.to_numeric(sales["unit_price"], errors="coerce")
sales["revenue"] = sales["quantity"] * sales["unit_price"]

print("\n" + "=" * 60)
print("BUSINESS SUMMARY")
print("=" * 60)
print("Total revenue:", round(sales["revenue"].sum(), 2))
print("Unique orders:", sales["order_id"].nunique())
print("Total quantity:", sales["quantity"].sum())

print("\nTop 10 products by revenue:")
print(
    sales.groupby("product_name")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
