import pandas as pd
from sqlalchemy.orm import sessionmaker
from database import engine
from models import SalesTransaction, Transaction,Product,Customer
Session = sessionmaker(bind=engine)
session = Session()
df1 = pd.read_csv("../sales_data_prepped.csv")
df1['Date'] = pd.to_datetime(df1['Date'])

product_df = pd.read_csv("../product_lookup.csv")

for _, row in product_df.iterrows():
    product = Product(
        product_id=row['Product ID'],
        category=row['Category']
    )
    session.add(product)

session.commit()
print("Loaded products")
for _,row in df1.iterrows():
    record = SalesTransaction(
        store_id=row['Store ID'],
        product_id=row['Product ID'],
        date=row['Date'],
        units_sold=row['Units Sold'],
        inventory_level=row['Inventory Level'],
        demand=row['Demand']
    )
    session.add(record);

session.commit()
print(f"Loaded {len(df1)} rows into Sales Transactions")

df2 = pd.read_csv("../retail_sales_data_prepped.csv")
df2['Date'] = pd.to_datetime(df2['Date'])

for _, row in (df2[['Customer ID', 'Gender', 'Age']].drop_duplicates()).iterrows():
    customer = Customer(
        customer_id=row['Customer ID'],
        gender=row['Gender'],
        age=row['Age']
    )
    session.add(customer)

session.commit()
print("Loaded customers")

for _,row in df2.iterrows():
    record = Transaction(
        customer_id=row['Customer ID'],
        date=row['Date'],
        product_category=row['Product Category'],
        quantity=row['Quantity'],
        price_per_unit=row['Price per Unit'],
        total_amount=row['Total Amount'],
    )
    session.add(record);

session.commit()
print(f"Loaded {len(df2)} rows into Transactions")
session.close()


