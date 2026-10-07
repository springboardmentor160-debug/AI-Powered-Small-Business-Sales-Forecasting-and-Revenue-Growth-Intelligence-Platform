import pandas as pd
from sqlalchemy.orm import sessionmaker
from database import engine
from models import SalesTransaction, Transaction, Product, Customer

Session = sessionmaker(bind=engine)
session = Session()

# ---------------------------------------------------------------------------
# sales_data_prepped.csv -> products, sales_transactions
# (unchanged from M1 -- still the inventory/forecasting dataset)
# ---------------------------------------------------------------------------
df1 = pd.read_csv("../datasets/processed/sales_data_prepped.csv")
df1["Date"] = pd.to_datetime(df1["Date"])

product_df = pd.read_csv("../datasets/processed/product_lookup.csv")
for _, row in product_df.iterrows():
    session.add(Product(
        product_id=row["Product ID"],
        category=row["Category"],
    ))
session.commit()
print("Loaded products")

for _, row in df1.iterrows():
    session.add(SalesTransaction(
        store_id=row["Store ID"],
        product_id=row["Product ID"],
        date=row["Date"],
        units_sold=row["Units Sold"],
        inventory_level=row["Inventory Level"],
        demand=row["Demand"],
    ))
session.commit()
print(f"Loaded {len(df1)} rows into sales_transactions")

# ---------------------------------------------------------------------------
# online_retail_prepped.csv -> customers, transactions
# (M2 -- replaces retail_sales_dataset_final.csv as the customer source)
# ---------------------------------------------------------------------------
df2 = pd.read_csv("../datasets/processed/online_retail_prepped.csv")
df2["InvoiceDate"] = pd.to_datetime(df2["InvoiceDate"])
df2["CustomerID"] = df2["CustomerID"].astype(str)

# One row per unique customer -- Country is the only per-customer field
# available in this dataset. If a customer appears under more than one
# country (a handful do, e.g. travel/relocation), the first one seen is
# used; this is a minor, acceptable simplification for a single-country
# field on a segmentation-support table.
customer_df = df2[["CustomerID", "Country"]].drop_duplicates(subset=["CustomerID"])
for _, row in customer_df.iterrows():
    session.add(Customer(
        customer_id=row["CustomerID"],
        country=row["Country"],
    ))
session.commit()
print(f"Loaded {len(customer_df)} customers")

for _, row in df2.iterrows():
    session.add(Transaction(
        invoice_no=row["InvoiceNo"],
        stock_code=row["StockCode"],
        description=row["Description"],
        customer_id=row["CustomerID"],
        date=row["InvoiceDate"],
        quantity=row["Quantity"],
        unit_price=row["UnitPrice"],
        total_amount=row["TotalAmount"],
    ))
session.commit()
print(f"Loaded {len(df2)} rows into transactions")

session.close()