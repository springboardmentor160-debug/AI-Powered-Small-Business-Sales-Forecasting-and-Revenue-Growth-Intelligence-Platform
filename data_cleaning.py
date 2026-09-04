import pandas as pd

df = pd.read_excel("data/Online Retail.xlsx")

print("Original dataset shape:", df.shape)


df = df.drop_duplicates()

print("After removing duplicates:", df.shape)

df = df.dropna(subset=["CustomerID"])

print("After removing missing CustomerID:", df.shape)


df = df.dropna(subset=["Description"])

print("After removing missing Description:", df.shape)


df = df[df["Quantity"] > 0]

print("After removing invalid quantities:", df.shape)


df = df[df["UnitPrice"] > 0]

print("After removing invalid prices:", df.shape)



df["Revenue"] = df["Quantity"] * df["UnitPrice"]


df["CustomerID"] = df["CustomerID"].astype(int)


df.to_csv("data/clean_retail_sales.csv", index=False)


print("\n--- CLEAN DATASET ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATES ---")
print(df.duplicated().sum())

print("\n--- FIRST 5 CLEAN RECORDS ---")
print(df.head())

print("\nClean dataset saved successfully!")

print("\n--- CLEAN DATASET CHECK ---")

print("Rows:", len(df))
print("Customers:", df["CustomerID"].nunique())
print("Products:", df["StockCode"].nunique())

print("Minimum Quantity:", df["Quantity"].min())
print("Minimum Unit Price:", df["UnitPrice"].min())
print("Minimum Revenue:", df["Revenue"].min())


customer_data = df.groupby("CustomerID").agg(
    country=("Country", "first"),
    total_orders=("InvoiceNo", "nunique"),
    total_quantity=("Quantity", "sum"),
    total_spending=("Revenue", "sum")
).reset_index()

# Save customer dataset
customer_data.to_csv("data/clean_customers.csv", index=False)

print("\n--- CUSTOMER DATASET ---")
print(customer_data.head())

print("\nNumber of customers:", len(customer_data))

print("\nCustomer dataset saved successfully!")


product_data = df.groupby("StockCode").agg(
    description=("Description", "first"),
    total_quantity_sold=("Quantity", "sum"),
    total_revenue=("Revenue", "sum")
).reset_index()

product_data.to_csv("data/clean_products.csv", index=False)

print("\n--- PRODUCT DATASET ---")
print(product_data.head())

print("\nNumber of products:", len(product_data))

print("\nProduct dataset saved successfully!")